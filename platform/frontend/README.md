# projectome-atlas

An interactive web viewer for single-neuron **projectome** atlases. This open-source
release supports **mouse** and **macaque** (code name `monkey`) species.

> Note: the `fish` (zebrafish) environment and the mouse `rbm` / `trimodal`
> sub-variants are **not** part of this public release.

## Neuron Data

This repository contains the frontend/backend **code** only — it does not include the
SWC neuron morphology data itself, nor the gRPC-based streaming service (mentioned in the
paper's Methods) that serves neuron/region data to the 3D viewport at runtime.

By default, the interactive 3D viewport connects to the ProjAtlas platform's own public
data service via `VUE_APP_NEUROVIZ` / `VUE_APP_NEUROVIZ_SRV` in `.env.<mode>` (see
`.env.example`) — no separate data backend setup is required to browse the existing
platform. That service is not part of this repository.

If you want to work with the raw SWC data directly (e.g. for offline analysis or to build
your own data service), the full mouse and macaque single-neuron projectome datasets
(45,754 mouse + 2,231 macaque neurons, standard SWC format with metadata) are publicly
available for download from the ProjAtlas web portals:

- Mouse: https://mouse.digital-brain.cn/projectome/download
- Macaque: https://macaque.digital-brain.cn/projectome/download

## Project setup

```bash
npm install
```

## Environment configuration

All runtime configuration lives in `.env.<mode>` files (loaded via
[Vue CLI modes](https://cli.vuejs.org/guide/modes-and-env.html)). The real
`.env.*` files are **not** committed — only `.env.example` is. To run locally:

```bash
cp .env.example .env.development_mouse
# then edit .env.development_mouse and fill in YOUR server URLs
```

### Supported modes (species)

| Mode                   | `VUE_APP_TARGET` | `VUE_APP_SUB_SPECIES` | Species      |
| ---------------------- | ---------------- | --------------------- | ------------ |
| `development_mouse`    | `mouse`          | _(empty)_             | Mouse        |
| `beta_mouse`           | `mouse`          | _(empty)_             | Mouse        |
| `production_mouse`     | `mouse`          | _(empty)_             | Mouse        |
| `staging_mouse`        | `mouse`          | _(empty)_             | Mouse        |
| `staging_macaque`      | `monkey`         | _(empty)_             | Macaque      |
| `production_macaque`   | `monkey`         | _(empty)_             | Macaque      |

In the source code, **macaque is referenced as `"monkey"`** — keep that in mind
when reading `process.env.VUE_APP_TARGET` checks.

### Optional external links

The following variables are **optional**. Leave them blank to disable the
corresponding link — by default the build links to **no internal host**:

- `VUE_APP_HELP_URL` — help / docs page
- `VUE_APP_CONTACT_URL` — contact page
- `VUE_APP_DATACENTER_URL` — data portal base (dataset detail links)
- `VUE_APP_ASSETS_URL` — static asset CDN base (e.g. tutorial videos)
- `VUE_APP_ANALYTICS_URL` — Matomo analytics base; **unset = no tracking**

## Scripts

```bash
npm run serve                 # dev server, mouse (development_mouse)
npm run dev                   # alias for mouse dev (openssl-legacy-provider)
npm run dev_prod             # mouse, production_mouse mode
npm run dev_macaque          # macaque dev (staging_macaque)
npm run serve-macaque        # macaque dev (staging_macaque)
npm run build                # production build, mouse (staging_mouse)  ← default build
npm run build-mouse-beta     # mouse, beta_mouse
npm run build-mouse-production   # mouse, production_mouse
npm run build-macaque        # macaque, staging_macaque
npm run build-macaque-production  # macaque, production_macaque
npm run lint                 # lint
npm run lint-fix             # lint + autofix
```

> Requires Node 14–16 (the build uses `--openssl-legacy-provider` for OpenSSL 3
> compatibility).

## License

[MIT](./LICENSE)
