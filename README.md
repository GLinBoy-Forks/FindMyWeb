# FindMyWeb
A project which allows you to build trackers which you actually own. The idea is to create a way for you to build your own trackers using the already existing networks without requiring you to own any vendor specific devices.

## Supported networks
- [x] Apple FindMy
- [ ] Google Find My Device
- [ ] Samsung SmartThings

## Why
Currently there are a lot of different networks for location trackers from a plethora of different vendors. This causes a lot of fragmantation and everyone requires you to own a device where their closed-source software runs without you knowing what actually happens with your location. The idea is to create a web interaface for all of them and allow you to build your own open-source trackers.

## How
The backend currently uses malmeloss FindMy.py library to interact with Apples network while the trackers run a custom Zephyr based firmware. You can find out more info in the setup instructions.

# Setup
## Web (Frontend+Backend)
- [Development/Baremetal](docs/server/development.md)
- [Docker](docs/server/docker.md) (TBD)

## FruityTag (Firmware)
- [Building](docs/firmware/building.md)
- [Prebuilt](docs/firmware/prebuilt.md) (TBD)

# Thanks
- [seemo-lab](https://github.com/seemoo-lab/openhaystack/) for their initial research on the FindMy network
- [malmeloo](https://floss.social/@dismissed) for his excellent [FindMy.py](https://github.com/malmeloo/FindMy.py) library
