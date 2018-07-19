# :spades: Spade :spades:

A Python script that identifies any RHEL8 modules that depend on other modules to help populate the blacklist.  Running it will return the module with its ID and the dependency it has in the blacklist.yaml file.

To install the necessary packages, run:
```bash
sudo dnf install python-gobject

sudo dnf install libmodulemd
```

To choose what dependencies would warrant a blacklist on a particular module, populate the blacklist.yaml file with the appropriate requires and buildrequires dependencies.

