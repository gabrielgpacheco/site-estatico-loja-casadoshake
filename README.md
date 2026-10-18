# Loja Casa do Shake (catálogo estático)

Catálogo de produtos da Casa do Shake — Cabo Frio. Site estático, sem servidor,
sem banco e sem checkout: cada produto tem um botão que abre o WhatsApp com a
mensagem pronta.

- Site: https://loja.casadoshake.com.br
- WhatsApp: https://wa.me/5522981757472

## Estrutura

```
index.html              catálogo (busca + filtro por categoria)
produto/<slug>.html     página de cada produto
assets/css/style.css    estilos (tokens da marca)
assets/js/site.js       busca, filtro, galeria e seletor de variação
assets/img/             imagens otimizadas (thumb 520px / large 1100px, WebP)
catalog.json            dados dos produtos
tools/                  scripts de extração, otimização e build
```

## Pipeline (regenerar)

```powershell
python tools/extract_catalog.py
node  tools/optimize_images.js
python tools/build_site.py
npx --yes serve .
```

## Deploy

Hospedado no GitHub Pages (branch `main`, raiz); o domínio é definido pelo arquivo `CNAME`.
