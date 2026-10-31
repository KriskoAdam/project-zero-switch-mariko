/* ABI declarations copied from the verified libmtp 1.1.23 source distribution
 * (src/ptp.h). These are internal, version-specific interfaces, not public API. */
#ifndef LIBMTP_PTP_ABI_H
#define LIBMTP_PTP_ABI_H
#include <stdint.h>

typedef struct {
    uint16_t StandardVersion;
    uint32_t VendorExtensionID;
    uint16_t VendorExtensionVersion;
    char *VendorExtensionDesc;
    uint16_t FunctionalMode;
    uint32_t OperationsSupported_len;
    uint16_t *OperationsSupported;
    uint32_t EventsSupported_len;
    uint16_t *EventsSupported;
    uint32_t DevicePropertiesSupported_len;
    uint16_t *DevicePropertiesSupported;
    uint32_t CaptureFormats_len;
    uint16_t *CaptureFormats;
    uint32_t ImageFormats_len;
    uint16_t *ImageFormats;
    char *Manufacturer;
    char *Model;
    char *DeviceVersion;
    char *SerialNumber;
} PZ_PTPDeviceInfo;

typedef struct {
    uint32_t n;
    uint32_t *Storage;
} PZ_PTPStorageIDs;

typedef struct {
    uint16_t StorageType;
    uint16_t FilesystemType;
    uint16_t AccessCapability;
    uint64_t MaxCapability;
    uint64_t FreeSpaceInBytes;
    uint32_t FreeSpaceInImages;
    char *StorageDescription;
    char *VolumeLabel;
} PZ_PTPStorageInfo;

extern uint16_t ptp_getdeviceinfo(void *, PZ_PTPDeviceInfo *);
extern uint16_t ptp_getstorageids(void *, PZ_PTPStorageIDs *);
extern uint16_t ptp_getstorageinfo(void *, uint32_t, PZ_PTPStorageInfo *);
extern uint16_t ptp_getnumobjects(void *, uint32_t, uint32_t, uint32_t, uint32_t *);

#define PZ_PTP_RC_OK 0x2001
#define PZ_PTP_RC_INVALID_OBJECT_HANDLE 0x2009
#define PZ_PTP_OC_GET_DEVICE_INFO 0x1001
#define PZ_PTP_OC_GET_STORAGE_IDS 0x1004
#define PZ_PTP_OC_GET_STORAGE_INFO 0x1005
#define PZ_PTP_OC_GET_NUM_OBJECTS 0x1006
#define PZ_PTP_OC_GET_DEVICE_PROP_DESC 0x1014
#define PZ_PTP_OC_GET_DEVICE_PROP_VALUE 0x1015
#define PZ_PTP_ROOT_PARENT 0xffffffffu

#endif
