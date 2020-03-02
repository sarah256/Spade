# :spades: Spade :spades:

A Python script that identifies any modules that depend on other modules by parsing a module's ModuleMD and comparing the set of buildrequires and requires to the blacklist of modules.  Running it will return the module with its ID and the dependency it has in the blacklist.yaml file.

To install the necessary packages, run:
```bash
sudo dnf -y install python3-gobject libmodulemd python3-pygit2 python3-yamlordereddictloader
```

To choose what dependencies would warrant a blacklist on a particular module, populate the blacklist.yaml file with the appropriate requires and buildrequires dependencies.

