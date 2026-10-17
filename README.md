# Loja Casa do Shake (catálogo estático)

Catálogo de produtos da Casa do Shake — Cabo Frio, migrado do WooCommerce
(`loja.casadoshake.com.br`) para site estático. Sem servidor, sem banco, sem
checkout: cada produto tem um botão que abre o WhatsApp com a mensagem pronta.

- Site: https://loja.casadoshake.com.br
- WhatsApp: https://wa.me/5522981757472

## Estrutura

```
index.html              catálogo (busca + filtro por categoria)
produto/<slug>.html     página de cada produto
assets/css/style.css    estilos (tokens da marca)
assets/js/site.js       busca, filtro, galeria e seletor de variação
assets/img/             imagens otimizadas (thumb 520px / large 1100px, WebP)
assets/src/             imagens originais extraídas do backup (gitignored)
catalog.json            dados extraídos do banco da loja
tools/                  scripts de extração, otimização e build
```

## Pipeline (regenerar)

Fonte: backup cPanel da loja (pasta `../Casa do Shake`, não versionada).

```powershell
python tools/extract_catalog.py      # dump .sql.gz -> catalog.json
node  tools/optimize_images.js       # catalog.json -> assets/img/*.webp
python tools/build_site.py           # catalog.json -> HTML/CSS/JS
npx --yes serve .                    # preview local
```

## Deploy

GitHub Pages (branch `main`, raiz). `CNAME` = `loja.casadoshake.com.br`.
DNS: `CNAME loja -> <usuario>.github.io`. Ativar Enforce HTTPS.
