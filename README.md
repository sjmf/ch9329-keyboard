# CH9329 keyboard controller script

A script to send keyboard commands over a UART serial connection to a CH9329 Uart to USB HID keyboard controller. You can find these from vendors on eBay and aliexpress for next to nothing. However, there is very little software support available for these modules and the protocol documentation is written in Chinese. 

This Python script includes several methods to capture keyboard scan codes from a keyboard attached to the local computer where the script is running, and send them via Serial UART to the device which the USB HID keyboard is listening on.

Some capture methods require superuser privileges (`sudo`), for example `pyusb` provides the most accurate keyboard scancode capture, but needs to de-register the device driver for the input method in order to control it directly.

