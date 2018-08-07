# galileo-blocks

## Setup

Requirements:
- `singularity` (https://github.com/singularityware/singularity)

Steps:

1. Setup singularity

2. Build container

```bash
cd /singularity
chmod +x build_container.sh
./build_container env.simg Singularity
```

## Testing

Still in development. Only expect `tests` to run

```bash
cd /tests
chmod +x run_test.sh
./run_test.sh <some_test>.py <args> (use --help)
```


