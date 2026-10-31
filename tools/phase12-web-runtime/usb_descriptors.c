#include <libusb.h>
#include <stdio.h>

/* Read standard USB descriptor metadata only. This program does not open or
 * claim the device, and does not send MTP or endpoint data transfers. */
int main(void) {
    libusb_context *ctx = NULL;
    libusb_device **devices = NULL;
    ssize_t count;
    int matches = 0;

    int rc = libusb_init(&ctx);
    if (rc != 0) {
        fprintf(stderr, "libusb_init: %s\n", libusb_error_name(rc));
        return 1;
    }

    count = libusb_get_device_list(ctx, &devices);
    if (count < 0) {
        fprintf(stderr, "libusb_get_device_list: %s\n",
                libusb_error_name((int)count));
        libusb_exit(ctx);
        return 1;
    }

    for (ssize_t i = 0; i < count; ++i) {
        struct libusb_device_descriptor d;
        rc = libusb_get_device_descriptor(devices[i], &d);
        if (rc != 0 || d.idVendor != 0x057e || d.idProduct != 0x201d)
            continue;

        ++matches;
        printf("Nintendo Switch VID:PID %04x:%04x\n", d.idVendor, d.idProduct);
        printf("USB %x.%02x, device release %x.%02x, configurations %u\n",
               d.bcdUSB >> 8, d.bcdUSB & 0xff,
               d.bcdDevice >> 8, d.bcdDevice & 0xff,
               d.bNumConfigurations);

        struct libusb_config_descriptor *cfg = NULL;
        rc = libusb_get_active_config_descriptor(devices[i], &cfg);
        if (rc != 0) {
            fprintf(stderr, "active config descriptor: %s\n",
                    libusb_error_name(rc));
            continue;
        }
        printf("Active configuration value %u, interfaces %u\n",
               cfg->bConfigurationValue, cfg->bNumInterfaces);
        for (uint8_t n = 0; n < cfg->bNumInterfaces; ++n) {
            const struct libusb_interface *iface = &cfg->interface[n];
            for (int a = 0; a < iface->num_altsetting; ++a) {
                const struct libusb_interface_descriptor *alt =
                    &iface->altsetting[a];
                printf("Interface %u alt %u class/subclass/protocol %02x/%02x/%02x, endpoints %u\n",
                       alt->bInterfaceNumber, alt->bAlternateSetting,
                       alt->bInterfaceClass, alt->bInterfaceSubClass,
                       alt->bInterfaceProtocol, alt->bNumEndpoints);
                for (uint8_t e = 0; e < alt->bNumEndpoints; ++e) {
                    const struct libusb_endpoint_descriptor *ep =
                        &alt->endpoint[e];
                    const char *direction =
                        (ep->bEndpointAddress & LIBUSB_ENDPOINT_DIR_MASK) ==
                                LIBUSB_ENDPOINT_IN ? "IN" : "OUT";
                    const char *type;
                    switch (ep->bmAttributes & LIBUSB_TRANSFER_TYPE_MASK) {
                    case LIBUSB_TRANSFER_TYPE_BULK: type = "bulk"; break;
                    case LIBUSB_TRANSFER_TYPE_INTERRUPT: type = "interrupt"; break;
                    case LIBUSB_TRANSFER_TYPE_ISOCHRONOUS: type = "isochronous"; break;
                    default: type = "control/unknown"; break;
                    }
                    printf("  endpoint 0x%02x %s %s max-packet %u interval %u\n",
                           ep->bEndpointAddress, direction, type,
                           ep->wMaxPacketSize, ep->bInterval);
                }
            }
        }
        libusb_free_config_descriptor(cfg);
    }

    libusb_free_device_list(devices, 1);
    libusb_exit(ctx);
    if (matches == 0) {
        fprintf(stderr, "Nintendo Switch 057e:201d not found\n");
        return 2;
    }
    return 0;
}
