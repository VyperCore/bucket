WORK IN PROGRESS

To run

```
$ poetry install
$ poetry shell
$ python -m bucket.example
$ cd viewer
# These symlinks are required due to the way we currently bind in
# python - but later we will replace that mechanism with a server
$ ln -s ../bucket bucket
$ ln -s ../example_file_store.db example_file_store.db
$ npm install
$ npm run dev
^ Go to listed address
```
