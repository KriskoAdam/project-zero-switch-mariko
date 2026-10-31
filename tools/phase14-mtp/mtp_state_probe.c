#include <libmtp.h>
#include "../PHASE_13/libmtp_ptp_abi.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_DEVICE_LIST 256u
#define MAX_STORAGE_LIST 32u

static void timestamp(char out[40]) {
    struct timespec ts;
    struct tm tmv;
    clock_gettime(CLOCK_REALTIME, &ts);
    localtime_r(&ts.tv_sec, &tmv);
    strftime(out, 24, "%Y-%m-%dT%H:%M:%S", &tmv);
    snprintf(out + 19, 21, ".%03ld%+03ld%02ld", ts.tv_nsec / 1000000,
             tmv.tm_gmtoff / 3600, labs((tmv.tm_gmtoff / 60) % 60));
}

static void js(const char *s, size_t cap) {
    putchar('"');
    if (s) {
        size_t n = strnlen(s, cap);
        for (size_t i = 0; i < n; ++i) {
            unsigned char c = (unsigned char)s[i];
            if (c == '"' || c == '\\') { putchar('\\'); putchar(c); }
            else if (c == '\n') fputs("\\n", stdout);
            else if (c == '\r') fputs("\\r", stdout);
            else if (c == '\t') fputs("\\t", stdout);
            else if (c < 0x20) printf("\\u%04x", c);
            else putchar(c);
        }
        if (n == cap) fputs("[TRUNCATED]", stdout);
    }
    putchar('"');
}

static const char *rc_name(uint16_t rc) {
    if (rc == PZ_PTP_RC_OK) return "OK";
    if (rc == PZ_PTP_RC_INVALID_OBJECT_HANDLE) return "InvalidObjectHandle";
    return "OtherResponse";
}

static const char *op_name(uint16_t op) {
    switch (op) {
    case 0x1001: return "GetDeviceInfo";
    case 0x1002: return "OpenSession";
    case 0x1003: return "CloseSession";
    case 0x1004: return "GetStorageIDs";
    case 0x1005: return "GetStorageInfo";
    case 0x1006: return "GetNumObjects";
    case 0x1007: return "GetObjectHandles";
    case 0x1008: return "GetObjectInfo";
    case 0x1009: return "GetObject";
    case 0x100a: return "GetThumb";
    default: return "Other";
    }
}

static int advertised(const PZ_PTPDeviceInfo *di, uint16_t code) {
    for (uint32_t i = 0; i < di->OperationsSupported_len; ++i)
        if (di->OperationsSupported[i] == code) return 1;
    return 0;
}

static int valid_list(uint32_t n, const void *p) {
    return n <= MAX_DEVICE_LIST && (n == 0 || p != NULL);
}

static void event(const char *state, int trial, const char *kind,
                  const char *name, uint16_t code, int supported,
                  int performed, int response, const char *start,
                  const char *finish) {
    printf("{\"state\":"); js(state, 32);
    printf(",\"trial\":%d,\"kind\":", trial); js(kind, 32);
    if (name) { printf(",\"operation\":"); js(name, 80); }
    if (code) printf(",\"operation_code\":\"0x%04x\",", code);
    if (name) printf("\"declared_supported\":%s,\"performed\":%s,",
                     supported ? "true" : "false", performed ? "true" : "false");
    printf("\"started_at\":"); js(start, 40);
    printf(",\"finished_at\":"); js(finish, 40);
    if (performed) printf(",\"response_code\":\"0x%04x\",\"response_name\":\"%s\"",
                          (unsigned)response, rc_name((uint16_t)response));
    puts("}");
}

static void free_device_info(PZ_PTPDeviceInfo *d) {
    free(d->VendorExtensionDesc); free(d->OperationsSupported);
    free(d->EventsSupported); free(d->DevicePropertiesSupported);
    free(d->CaptureFormats); free(d->ImageFormats);
    free(d->Manufacturer); free(d->Model); free(d->DeviceVersion);
    free(d->SerialNumber);
    memset(d, 0, sizeof(*d));
}

static int run_trial(LIBMTP_raw_device_t *raw, const char *state, int trial) {
    char start[40], finish[40];
    LIBMTP_mtpdevice_t *dev;
    PZ_PTPDeviceInfo di = {0};
    PZ_PTPStorageIDs ids = {0};
    int result = 0;

    timestamp(start);
    dev = LIBMTP_Open_Raw_Device(raw); /* opens USB and standard MTP session */
    timestamp(finish);
    printf("{\"state\":"); js(state, 32);
    printf(",\"trial\":%d,\"kind\":\"session_open\",\"operation\":\"OpenSession\","
           "\"operation_code\":\"0x1002\",\"declared_supported\":true,"
           "\"performed\":true,\"library_open_succeeded\":%s,"
           "\"raw_response_code_exposed\":false,\"started_at\":", trial,
           dev ? "true" : "false");
    js(start, 40); printf(",\"finished_at\":"); js(finish, 40); puts("}");
    if (!dev) return 1;

    timestamp(start);
    uint16_t rc = ptp_getdeviceinfo(dev->params, &di);
    timestamp(finish);
    event(state, trial, "operation", "GetDeviceInfo", 0x1001,
          advertised(&di, 0x1001), 1, rc, start, finish);
    if (rc != PZ_PTP_RC_OK ||
        !valid_list(di.OperationsSupported_len, di.OperationsSupported) ||
        !valid_list(di.EventsSupported_len, di.EventsSupported) ||
        !valid_list(di.DevicePropertiesSupported_len, di.DevicePropertiesSupported) ||
        !valid_list(di.CaptureFormats_len, di.CaptureFormats) ||
        !valid_list(di.ImageFormats_len, di.ImageFormats)) {
        fprintf(stderr, "Unsafe or failed DeviceInfo dataset; aborting trial %d.\n", trial);
        result = 2; goto release;
    }

    printf("{\"state\":"); js(state, 32);
    printf(",\"trial\":%d,\"kind\":\"device_info\",\"standard_version\":%u,"
           "\"vendor_extension_id\":\"0x%08" PRIx32 "\",\"vendor_extension_version\":%u,"
           "\"vendor_extension_description\":",
           trial, di.StandardVersion, di.VendorExtensionID, di.VendorExtensionVersion);
    js(di.VendorExtensionDesc, 256);
    printf(",\"manufacturer\":"); js(di.Manufacturer, 256);
    printf(",\"model\":"); js(di.Model, 256);
    printf(",\"device_version\":"); js(di.DeviceVersion, 256);
    printf(",\"operations_supported\":[");
    for (uint32_t i = 0; i < di.OperationsSupported_len; ++i) {
        if (i) putchar(',');
        printf("{\"code\":\"0x%04x\",\"name\":", di.OperationsSupported[i]);
        js(op_name(di.OperationsSupported[i]), 80); putchar('}');
    }
    printf("],\"events_supported\":[");
    for (uint32_t i = 0; i < di.EventsSupported_len; ++i) {
        if (i) putchar(','); printf("\"0x%04x\"", di.EventsSupported[i]);
    }
    printf("],\"device_properties_supported\":[");
    for (uint32_t i = 0; i < di.DevicePropertiesSupported_len; ++i) {
        if (i) putchar(','); printf("\"0x%04x\"", di.DevicePropertiesSupported[i]);
    }
    puts("]}");

    if (advertised(&di, PZ_PTP_OC_GET_STORAGE_IDS)) {
        timestamp(start); rc = ptp_getstorageids(dev->params, &ids); timestamp(finish);
        event(state, trial, "operation", "GetStorageIDs", 0x1004, 1, 1, rc, start, finish);
    } else {
        timestamp(start); timestamp(finish);
        event(state, trial, "operation", "GetStorageIDs", 0x1004, 0, 0, 0, start, finish);
    }
    if (rc != PZ_PTP_RC_OK) { result = 3; goto release; }
    if (ids.n > MAX_STORAGE_LIST || (ids.n > 0 && ids.Storage == NULL)) {
        fprintf(stderr, "Unsafe StorageIDs dataset (%" PRIu32 "); aborting trial %d.\n", ids.n, trial);
        result = 4; goto release;
    }
    printf("{\"state\":"); js(state, 32);
    printf(",\"trial\":%d,\"kind\":\"storage_ids\",\"ids\":[", trial);
    for (uint32_t i = 0; i < ids.n; ++i) {
        if (i) putchar(','); printf("\"0x%08" PRIx32 "\"", ids.Storage[i]);
    }
    puts("]}");

    for (uint32_t i = 0; i < ids.n; ++i) {
        if (!advertised(&di, PZ_PTP_OC_GET_STORAGE_INFO)) break;
        PZ_PTPStorageInfo si = {0};
        timestamp(start); rc = ptp_getstorageinfo(dev->params, ids.Storage[i], &si); timestamp(finish);
        event(state, trial, "operation", "GetStorageInfo", 0x1005, 1, 1, rc, start, finish);
        printf("{\"state\":"); js(state, 32);
        printf(",\"trial\":%d,\"kind\":\"storage_info\",\"storage_id\":\"0x%08"
               PRIx32 "\",\"response_code\":\"0x%04x\",\"storage_type\":%u,"
               "\"filesystem_type\":%u,\"access_capability\":%u,\"max_capacity\":\"%"
               PRIu64 "\",\"free_space_bytes\":\"%" PRIu64 "\",\"free_space_in_images\":%"
               PRIu32 ",\"description\":",
               trial, ids.Storage[i], rc, si.StorageType, si.FilesystemType,
               si.AccessCapability, si.MaxCapability, si.FreeSpaceInBytes, si.FreeSpaceInImages);
        js(si.StorageDescription, 256); printf(",\"volume_label\":"); js(si.VolumeLabel, 256); puts("}");
        free(si.StorageDescription); free(si.VolumeLabel);
        if (rc != PZ_PTP_RC_OK) { result = 5; goto release; }

        if (advertised(&di, PZ_PTP_OC_GET_NUM_OBJECTS)) {
            uint32_t count = 0;
            timestamp(start);
            rc = ptp_getnumobjects(dev->params, ids.Storage[i], 0,
                                   PZ_PTP_ROOT_PARENT, &count);
            timestamp(finish);
            event(state, trial, "operation", "GetNumObjects", 0x1006, 1, 1, rc, start, finish);
            printf("{\"state\":"); js(state, 32);
            printf(",\"trial\":%d,\"kind\":\"object_count\",\"storage_id\":\"0x%08"
                   PRIx32 "\",\"format_code\":\"0x0000\",\"association_handle\":\"0xffffffff\","
                   "\"response_code\":\"0x%04x\",\"count\":",
                   trial, ids.Storage[i], rc);
            if (rc == PZ_PTP_RC_OK) printf("%" PRIu32, count); else fputs("null", stdout);
            puts("}");
            if (rc != PZ_PTP_RC_OK) { result = 6; goto release; }
        }
    }

release:
    free(ids.Storage);
    free_device_info(&di);
    timestamp(start);
    LIBMTP_Release_Device(dev); /* calls ptp_closesession, then closes USB */
    timestamp(finish);
    printf("{\"state\":"); js(state, 32);
    printf(",\"trial\":%d,\"kind\":\"session_close\",\"operation\":\"CloseSession\","
           "\"operation_code\":\"0x1003\",\"release_called\":true,\"release_api_returns_void\":true,"
           "\"raw_response_code_exposed\":false,\"started_at\":", trial);
    js(start, 40); printf(",\"finished_at\":"); js(finish, 40);
    puts("}");
    return result;
}

int main(int argc, char **argv) {
    const char *state = argc > 1 ? argv[1] : "A";
    int trials = argc > 2 ? atoi(argv[2]) : 3;
    if (trials < 1 || trials > 10 || strlen(state) > 32) {
        fprintf(stderr, "Usage: %s STATE [1..10 trials]\n", argv[0]); return 64;
    }
    LIBMTP_Set_Debug(LIBMTP_DEBUG_NONE);
    LIBMTP_Init();
    LIBMTP_raw_device_t *raw = NULL;
    int nraw = 0;
    LIBMTP_error_number_t err = LIBMTP_Detect_Raw_Devices(&raw, &nraw);
    if (err != LIBMTP_ERROR_NONE || nraw <= 0) {
        fprintf(stderr, "No raw MTP devices detected (error=%d, count=%d).\n", err, nraw);
        free(raw); return 2;
    }
    LIBMTP_raw_device_t *target = NULL;
    for (int i = 0; i < nraw; ++i)
        if (raw[i].device_entry.vendor_id == 0x057e && raw[i].device_entry.product_id == 0x201d) {
            target = &raw[i]; break;
        }
    if (!target) {
        fprintf(stderr, "Nintendo MTP device 057e:201d not found.\n"); free(raw); return 3;
    }
    printf("{\"state\":"); js(state, 32);
    printf(",\"kind\":\"usb_identity\",\"vid\":\"0x%04x\",\"pid\":\"0x%04x\","
           "\"manufacturer\":", target->device_entry.vendor_id, target->device_entry.product_id);
    js(target->device_entry.vendor, 128); printf(",\"product\":"); js(target->device_entry.product, 128);
    puts("}");

    int result = 0;
    for (int trial = 1; trial <= trials; ++trial) {
        int rc = run_trial(target, state, trial);
        if (rc != 0) { result = rc; break; }
    }
    free(raw);
    return result;
}
