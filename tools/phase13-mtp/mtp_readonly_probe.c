#include <libmtp.h>
#include "libmtp_ptp_abi.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static void timestamp(char out[40]) {
    struct timespec ts;
    struct tm tmv;
    clock_gettime(CLOCK_REALTIME, &ts);
    localtime_r(&ts.tv_sec, &tmv);
    strftime(out, 24, "%Y-%m-%dT%H:%M:%S", &tmv);
    snprintf(out + 19, 21, ".%03ld%+03ld%02ld", ts.tv_nsec / 1000000,
             tmv.tm_gmtoff / 3600, labs((tmv.tm_gmtoff / 60) % 60));
}

static void js(const char *s) {
    putchar('"');
    if (s) for (; *s; ++s) {
        unsigned char c = (unsigned char)*s;
        if (c == '"' || c == '\\') { putchar('\\'); putchar(c); }
        else if (c == '\n') fputs("\\n", stdout);
        else if (c == '\r') fputs("\\r", stdout);
        else if (c == '\t') fputs("\\t", stdout);
        else if (c < 0x20) printf("\\u%04x", c);
        else putchar(c);
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

static void emit_operation(const char *name, uint16_t code, int supported,
                           int performed, int response, const char *start,
                           const char *finish) {
    printf("{\"kind\":\"operation\",\"operation\":"); js(name);
    printf(",\"operation_code\":\"0x%04x\",\"declared_supported\":%s,"
           "\"performed\":%s,\"started_at\":", code,
           supported ? "true" : "false", performed ? "true" : "false");
    js(start); printf(",\"finished_at\":"); js(finish);
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
}

int main(void) {
    LIBMTP_raw_device_t *raw = NULL;
    int nraw = 0, found = 0;
    LIBMTP_mtpdevice_t *dev = NULL;
    char start[40], finish[40];
    PZ_PTPDeviceInfo di = {0};
    PZ_PTPStorageIDs ids = {0};

    LIBMTP_Set_Debug(LIBMTP_DEBUG_NONE);
    LIBMTP_Init();
    LIBMTP_error_number_t detect = LIBMTP_Detect_Raw_Devices(&raw, &nraw);
    if (detect != LIBMTP_ERROR_NONE || nraw <= 0) {
        fprintf(stderr, "No MTP devices detected (error=%d count=%d)\n", detect, nraw);
        free(raw); return 2;
    }
    for (int i = 0; i < nraw; ++i) {
        if (raw[i].device_entry.vendor_id == 0x057e &&
            raw[i].device_entry.product_id == 0x201d) {
            found = 1; dev = LIBMTP_Open_Raw_Device(&raw[i]); break;
        }
    }
    free(raw);
    if (!found || !dev) {
        fprintf(stderr, "Nintendo Switch 057e:201d not opened as MTP\n");
        return 3;
    }

    timestamp(start);
    uint16_t dev_rc = ptp_getdeviceinfo(dev->params, &di);
    timestamp(finish);
    emit_operation("GetDeviceInfo", PZ_PTP_OC_GET_DEVICE_INFO,
                   advertised(&di, PZ_PTP_OC_GET_DEVICE_INFO), 1, dev_rc, start, finish);
    printf("{\"kind\":\"device_info\",\"standard_version\":%u,"
           "\"vendor_extension_id\":\"0x%08" PRIx32 "\","
           "\"vendor_extension_version\":%u,\"vendor_extension_description\":",
           di.StandardVersion, di.VendorExtensionID, di.VendorExtensionVersion);
    js(di.VendorExtensionDesc);
    printf(",\"functional_mode\":%u,\"manufacturer\":", di.FunctionalMode);
    js(di.Manufacturer); printf(",\"model\":"); js(di.Model);
    printf(",\"device_version\":"); js(di.DeviceVersion);
    printf(",\"operations_supported\":[");
    for (uint32_t i = 0; i < di.OperationsSupported_len; ++i) {
        if (i) putchar(',');
        printf("{\"code\":\"0x%04x\",\"name\":", di.OperationsSupported[i]);
        js(op_name(di.OperationsSupported[i])); putchar('}');
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

    if (dev_rc != PZ_PTP_RC_OK) {
        free_device_info(&di); LIBMTP_Release_Device(dev); return 4;
    }

    uint16_t ids_rc = 0;
    int storage_ids_supported = advertised(&di, PZ_PTP_OC_GET_STORAGE_IDS);
    if (storage_ids_supported) {
        timestamp(start);
        ids_rc = ptp_getstorageids(dev->params, &ids);
        timestamp(finish);
        emit_operation("GetStorageIDs", PZ_PTP_OC_GET_STORAGE_IDS, 1, 1,
                       ids_rc, start, finish);
    } else {
        timestamp(start); timestamp(finish);
        emit_operation("GetStorageIDs", PZ_PTP_OC_GET_STORAGE_IDS, 0, 0,
                       0, start, finish);
    }
    printf("{\"kind\":\"storage_ids\",\"ids\":[");
    if (ids_rc == PZ_PTP_RC_OK) for (uint32_t i = 0; i < ids.n; ++i) {
        if (i) putchar(','); printf("\"0x%08" PRIx32 "\"", ids.Storage[i]);
    }
    puts("]}");

    if (storage_ids_supported && ids_rc == PZ_PTP_RC_OK &&
        advertised(&di, PZ_PTP_OC_GET_STORAGE_INFO)) {
        for (uint32_t i = 0; i < ids.n; ++i) {
            PZ_PTPStorageInfo si = {0};
            timestamp(start);
            uint16_t si_rc = ptp_getstorageinfo(dev->params, ids.Storage[i], &si);
            timestamp(finish);
            emit_operation("GetStorageInfo", PZ_PTP_OC_GET_STORAGE_INFO, 1, 1,
                           si_rc, start, finish);
            printf("{\"kind\":\"storage_info\",\"storage_id\":\"0x%08"
                   PRIx32 "\",\"response_code\":\"0x%04x\",\"storage_type\":%u,"
                   "\"filesystem_type\":%u,\"access_capability\":%u,"
                   "\"max_capacity\":\"%" PRIu64 "\",\"free_space_bytes\":\"%"
                   PRIu64 "\",\"free_space_in_images\":%" PRIu32 ",\"description\":",
                   ids.Storage[i], si_rc, si.StorageType, si.FilesystemType,
                   si.AccessCapability, si.MaxCapability, si.FreeSpaceInBytes,
                   si.FreeSpaceInImages);
            js(si.StorageDescription); printf(",\"volume_label\":"); js(si.VolumeLabel); puts("}");
            free(si.StorageDescription); free(si.VolumeLabel);

            if (advertised(&di, PZ_PTP_OC_GET_NUM_OBJECTS)) {
                uint32_t object_count = 0;
                timestamp(start);
                uint16_t count_rc = ptp_getnumobjects(dev->params, ids.Storage[i],
                        0x00000000, PZ_PTP_ROOT_PARENT, &object_count);
                timestamp(finish);
                emit_operation("GetNumObjects (all formats, root)",
                        PZ_PTP_OC_GET_NUM_OBJECTS, 1, 1, count_rc, start, finish);
                printf("{\"kind\":\"object_count\",\"storage_id\":\"0x%08"
                       PRIx32 "\",\"format_code\":\"0x0000\","
                       "\"association_handle\":\"0xffffffff\",\"response_code\":\"0x%04x\",",
                       ids.Storage[i], count_rc);
                if (count_rc == PZ_PTP_RC_OK) printf("\"count\":%" PRIu32, object_count);
                else fputs("\"count\":null", stdout);
                puts("}");
            }
        }
    }

    int propdesc_supported = advertised(&di, PZ_PTP_OC_GET_DEVICE_PROP_DESC);
    int propvalue_supported = advertised(&di, PZ_PTP_OC_GET_DEVICE_PROP_VALUE);
    printf("{\"kind\":\"property_operations\",\"get_device_prop_desc_code\":\"0x%04x\","
           "\"get_device_prop_desc_declared\":%s,\"get_device_prop_value_code\":\"0x%04x\","
           "\"get_device_prop_value_declared\":%s,\"device_property_count\":%" PRIu32
           ",\"performed\":false,\"reason\":\"No property query was issued: device did not advertise these operations/properties.\"}\n",
           PZ_PTP_OC_GET_DEVICE_PROP_DESC, propdesc_supported ? "true" : "false",
           PZ_PTP_OC_GET_DEVICE_PROP_VALUE, propvalue_supported ? "true" : "false",
           di.DevicePropertiesSupported_len);

    free(ids.Storage);
    free_device_info(&di);
    LIBMTP_Release_Device(dev);
    return 0;
}
