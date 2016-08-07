#include "serial_handling.h"

#include <Arduino.h>
#include <errno.h>
#include <assert13.h>

uint16_t serial_readline(char *line, uint16_t line_size) {
    int bytes_read = 0;    // Number of bytes read from the serial port.

    // Read until we hit the maximum length, or a newline.
    // One less than the maximum length because we want to add a null terminator.
    while (bytes_read < line_size - 1) {
        while (Serial.available() == 0) {
            // There is no data to be read from the serial port.
            // Wait until data is available.
        }

        line[bytes_read] = (char) Serial.read();

        // A newline is given by \r or \n, or some combination of both
        // or the read may have failed and returned 0
        if ( line[bytes_read] == '\r' || line[bytes_read] == '\n' ||
             line[bytes_read] == 0 ) {
                // We ran into a newline character!  Overwrite it with \0
                break;    // Break out of this - we are done reading a line.
        } else {
            bytes_read++;
        }
    }

    // Add null termination to the end of our string.
    line[bytes_read] = '\0';
    return bytes_read;
}

uint16_t string_read_field(const char *str, uint16_t str_start, 
    char *field, uint16_t field_size, const char *sep) {

    // Want to read from the string until we encounter the separator.

    // Character that we are reading from the string.
    uint16_t str_index = str_start;    

    while (1) {
        if ( str[str_index] == '\0') {
            str_index++;  // signal off end of str
            break;
            }

        if ( field_size <= 1 ) break;

        if (strchr(sep, str[str_index])) {
            // field finished, skip over the separator character.
            str_index++;    
            break;
            }

        // Copy the string character into buffer and move over to next
        *field = str[str_index];    
        field++;
        field_size--;
        // Move on to the next character.
        str_index++;    
        }

    // Make sure to add NULL termination to our new string.
    *field = '\0';

    // Return the index of where the next token begins.
    return str_index;    
}

int32_t string_get_int(const char *str) {
    // Attempt to convert the string to an integer using strtol...
    int32_t val = strtol(str, NULL, 10);

    if (val == 0) {
        // Must check errno for possible error.
        if (errno == ERANGE) {
            Serial.print("string_get_int failed: "); Serial.println(str);
            assert13(0, errno);
        }
    }

    return val;
}
