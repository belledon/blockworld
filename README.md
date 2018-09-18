# galileo-blocks

## Setup

Requirements:
- `singularity` (https://github.com/singularityware/singularity)

Steps:

1. Run the setup script

This script will build the container and initialize a project config.

> NOTE: This requires sudo in order to build the container.
> After release, this will only use the 
```bash
chmod +x setup.sh
./setup.sh

```



2.  (Optional) Configure `config.yaml`

Feel free to change any of the project-wide variables found in
`/config.yaml`.

Listed variables:

- `data` : The path to storing output (which may also be used later as input).
All methods rely on using relative paths to this value.

## Running

You will find `run.sh` which can be used to run any python script in the
submodules.

Usage:

``` 
./run.sh <interpreter> <script> <args> 
```

- `interpreter`: Refers to the program to run in the container. 
Usually `python3`.

- `script`: The script to run.

- `args` : The arguments for the script.

In general you can use:

```bash
./run.sh python3 <script> --help
```

## Testing

Still in development. Only expect `tests` to run

```bash
cd /tests
chmod +x run_test.sh
./run_test.sh <some_test>.py <args> (use --help)
```


