from findmy import KeyPair
from findmy.errors import UnauthorizedError
from findmy.reports import (
    AppleAccount,
    AsyncAppleAccount,
    BaseAnisetteProvider,
    LoginState,
    SmsSecondFactorMethod,
    TrustedDeviceSecondFactorMethod,
    RemoteAnisetteProvider,
)
import asyncio
import sys

ACCOUNT_STORE = "account.json"
ANISETTE_SERVER = "http://localhost:6969"


async def _login_async(account: AsyncAppleAccount) -> None:
    email = input("email?  > ")
    password = input("passwd? > ")

    state = await account.login(email, password)

    if state == LoginState.REQUIRE_2FA:  # Account requires 2FA
        # This only supports SMS methods for now
        methods = await account.get_2fa_methods()

        # Print the (masked) phone numbers
        for i, method in enumerate(methods):
            if isinstance(method, TrustedDeviceSecondFactorMethod):
                print(f"{i} - Trusted Device")
            elif isinstance(method, SmsSecondFactorMethod):
                print(f"{i} - SMS ({method.phone_number})")

        ind = int(input("Method? > "))

        method = methods[ind]
        await method.request()
        code = input("Code? > ")

        # This automatically finishes the post-2FA login flow
        await method.submit(code)


async def get_account_async(anisette: BaseAnisetteProvider) -> AsyncAppleAccount:
    """Tries to restore a saved Apple account, or prompts the user for login otherwise. (async)"""
    acc = AsyncAppleAccount(anisette=anisette)
    acc_store = ACCOUNT_STORE
    try:
        acc.from_json(acc_store)
    except FileNotFoundError:
        await _login_async(acc)
        acc.to_json(acc_store)

    return acc


async def main(b64_adv_key: str):
    key_pair = KeyPair.from_b64(b64_adv_key)
    anisette = RemoteAnisetteProvider(ANISETTE_SERVER)
    acc = await get_account_async(anisette)
    while True:
        try:
            reports = await acc.fetch_last_reports(key_pair)
            print(reports)
            break
        except UnauthorizedError:
            await acc.close()
            acc = AsyncAppleAccount(anisette=anisette)
            await _login_async(acc)
            acc.to_json(ACCOUNT_STORE)
    await acc.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
