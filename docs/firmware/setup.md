# Board Setup
1. Ensure you have a software to interact with serial ports e.g. `screen`, [`PuTTY`](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
2. Connect to the board with baud `115200` e.g. `screen /dev/ttyACM0 115200`
3. Set the advertisement key with `findmy key set <base64 key>`
4. The board should automatically reset
5. Verify everything was successful with `findmy key get`
