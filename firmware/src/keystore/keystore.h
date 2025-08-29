#include <stddef.h>
#include <stdint.h>

#define KEYSTORE_PUBKEY_SIZE 28

int keystore_get_pubkey(uint8_t* pub_key, size_t len);
int keystore_set_pubkey(uint8_t* new_pub_key, size_t len);
int keystore_register();
int keystore_reset();
