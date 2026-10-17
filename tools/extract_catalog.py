#!/usr/bin/env python3
"""Extrai o catalogo da loja (WooCommerce) do dump MySQL do backup cPanel.

Fonte: casadosh_wp_uybjn.sql.gz (banco da loja, prefixo useTAfHG_).
Saida: catalog.json com categorias, produtos, variacoes, imagens e campos ACF.

Uso:
    python extract_catalog.py [--sql CAMINHO] [--out CAMINHO] [--include-drafts]
"""
import argparse
import gzip
import io
import json
import os
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

Q = chr(39)
BS = chr(92)
LP = chr(40)
RP = chr(41)

ESCAPES = {
    "n": "\n", "r": "\r", "t": "\t", "0": "\0", "Z": chr(26),
    "b": "\b", "f": "\f", '"': '"', "'": "'", BS: BS, "%": "%", "_": "_",
}


def parse_tuples(s):
    """Parser simples de lista de tuplas MySQL `(...),(...)`."""
    rows = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] != LP:
            i += 1
            continue
        i += 1
        vals = []
        while True:
            while i < n and s[i] in " \n\r\t":
                i += 1
            if i >= n:
                break
            c = s[i]
            if c == Q:
                i += 1
                buf = []
                while i < n:
                    ch = s[i]
                    if ch == BS:
                        nxt = s[i + 1] if i + 1 < n else ""
                        buf.append(ESCAPES.get(nxt, nxt))
                        i += 2
                        continue
                    if ch == Q:
                        if i + 1 < n and s[i + 1] == Q:
                            buf.append(Q)
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(ch)
                    i += 1
                vals.append("".join(buf))
            elif c == RP:
                i += 1
                break
            else:
                j = i
                while j < n and s[j] not in ",)":
                    j += 1
                vals.append(s[i:j].strip())
                i = j
            while i < n and s[i] in " \n\r\t":
                i += 1
            if i < n and s[i] == ",":
                i += 1
                continue
            elif i < n and s[i] == RP:
                i += 1
                break
            else:
                break
        rows.append(vals)
    return rows


def rows_for(sql_path, table):
    mark = "INSERT INTO `%s` (" % table
    out = []
    with gzip.open(sql_path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(mark):
                out.extend(parse_tuples(line.split(" VALUES ", 1)[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sql", default=r"C:\Users\dayan\Downloads\migracao-sites\Casa do Shake\casadosh_wp_uybjn.sql.gz")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "catalog.json"))
    ap.add_argument("--prefix", default="useTAfHG_")
    ap.add_argument("--include-drafts", action="store_true")
    args = ap.parse_args()

    P = args.prefix
    sql = args.sql

    # --- posts / postmeta ---
    posts = rows_for(sql, P + "posts")      # ID,author,date,...,post_type(20),mime(21)
    postmeta = rows_for(sql, P + "postmeta")  # meta_id,post_id,meta_key,meta_value
    terms = rows_for(sql, P + "terms")        # term_id, name, slug, term_group
    term_tax = rows_for(sql, P + "term_taxonomy")  # tt_id, term_id, taxonomy, desc, parent, count
    term_rel = rows_for(sql, P + "term_relationships")  # object_id, tt_id, order

    term_name = {r[0]: r[1] for r in terms}
    term_slug = {r[0]: r[2] for r in terms}
    tt_map = {r[0]: {"term_id": r[1], "taxonomy": r[2]} for r in term_tax}

    # object_id -> list of (taxonomy, term_id)
    obj_terms = {}
    for r in term_rel:
        info = tt_map.get(r[1])
        if not info:
            continue
        obj_terms.setdefault(r[0], []).append((info["taxonomy"], info["term_id"]))

    # meta por post
    meta = {}
    for r in postmeta:
        if len(r) < 4:
            continue
        meta.setdefault(r[1], {})[r[2]] = r[3]

    # index de posts
    by_id = {}
    for r in posts:
        if len(r) < 22:
            continue
        by_id[r[0]] = r

    def m(pid, key, default=None):
        return meta.get(pid, {}).get(key, default)

    # --- attachments (imagens) ---
    attachments = {}
    for r in posts:
        if len(r) < 22 or r[20] != "attachment":
            continue
        f = m(r[0], "_wp_attached_file")
        if not f:
            # fallback: extrair de guid depois de /uploads/
            guid = r[18] if len(r) > 18 else ""
            if "/uploads/" in guid:
                f = guid.split("/uploads/", 1)[1]
        attachments[r[0]] = {"file": f, "guid": r[18] if len(r) > 18 else "", "title": r[5]}

    # --- variacoes ---
    variations_by_parent = {}
    for r in posts:
        if len(r) < 22 or r[20] != "product_variation":
            continue
        pid = r[0]
        parent = r[17]
        attrs = {}
        for k, v in meta.get(pid, {}).items():
            if k.startswith("attribute_pa_"):
                attrs[k[len("attribute_"):]] = v
        variations_by_parent.setdefault(parent, []).append({
            "id": int(pid),
            "attrs": attrs,
            "price": m(pid, "_price"),
            "regular_price": m(pid, "_regular_price"),
            "sku": m(pid, "_sku"),
            "stock": m(pid, "_stock_status"),
            "image_id": m(pid, "_thumbnail_id"),
            "enabled": r[7],
        })

    # --- produtos ---
    products = []
    for r in posts:
        if len(r) < 22 or r[20] != "product":
            continue
        status = r[7]
        if status != "publish" and not args.include_drafts:
            continue
        pid = r[0]
        cats = []
        for tax, tid in obj_terms.get(pid, []):
            if tax == "product_cat":
                cats.append({"slug": term_slug.get(tid), "name": term_name.get(tid)})
        thumb = m(pid, "_thumbnail_id")
        gallery = m(pid, "_product_image_gallery", "") or ""
        gallery_ids = [g for g in gallery.split(",") if g]
        imgs = []
        if thumb and thumb in attachments:
            imgs.append(attachments[thumb]["file"])
        for g in gallery_ids:
            if g in attachments:
                imgs.append(attachments[g]["file"])
        variations = variations_by_parent.get(pid, [])
        products.append({
            "id": int(pid),
            "title": r[5],
            "slug": r[11],
            "status": status,
            "excerpt": r[6],
            "categories": cats,
            "price": m(pid, "_price"),
            "regular_price": m(pid, "_regular_price"),
            "sku": m(pid, "_sku"),
            "stock": m(pid, "_stock_status"),
            "thumbnail_id": thumb,
            "images": imgs,
            "variations": variations,
            "acf": {
                "visao_geral": m(pid, "visao_geral"),
                "beneficios": m(pid, "beneficios_e_funcionalidades"),
                "modo_de_uso": m(pid, "modo_de_uso"),
                "nutricional": m(pid, "informacoes_nutricionais_tabela"),
            },
        })

    products.sort(key=lambda p: p["id"])

    # --- categorias (somente as com produtos publicados) ---
    used = Counter()
    for p in products:
        for c in p["categories"]:
            used[c["slug"]] += 1
    categories = []
    for r in term_tax:
        if r[2] != "product_cat":
            continue
        slug = term_slug.get(r[1])
        categories.append({
            "term_id": int(r[0]),
            "name": term_name.get(r[1]),
            "slug": slug,
            "parent": int(r[4]),
            "count_db": int(r[5]),
            "count_published": used.get(slug, 0),
        })
    categories.sort(key=lambda c: c["name"])

    out = {
        "source": os.path.basename(sql),
        "whatsapp": "5522981757472",
        "categories": categories,
        "products": products,
        "attachments_total": len(attachments),
    }

    outpath = os.path.abspath(args.out)
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Saida:", outpath)
    print("Produtos:", len(products), "(publicados)" if not args.include_drafts else "(inclui rascunhos)")
    print("Categorias:", len(categories), "| com produtos:", sum(1 for c in categories if c["count_published"]))
    print("Attachments indexados:", len(attachments))
    total_imgs = sum(len(p["images"]) for p in products)
    total_vars = sum(len(p["variations"]) for p in products)
    print("Referencias de imagem nos produtos:", total_imgs, "| variacoes:", total_vars)


if __name__ == "__main__":
    main()
