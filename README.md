# server-remote-control
Remote power control by accessing BMI.

## Notice

- A server may be down even the PMI system says it's on.

## Supported Systems

- `inspur`

![inspur](docs/imgs/inspur.png)

- `supermicro`

API is the same as `inspur`.

![supermicro](docs/imgs/supermicro.png)

- `inspur_plain`

![inspur_plain](docs/imgs/inspur_plain.png)

- `megapoint`

![megapoint](docs/imgs/megapoint.png)

## QuickStart

```bash
alembic revision -m "update"
alembic upgrade head
```
