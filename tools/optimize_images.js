// Otimiza as imagens dos produtos: gera WebP em 2 tamanhos (thumb/large)
// e enriquece catalog.json com os caminhos otimizados.
//
// Uso: node optimize_images.js
const fs = require("fs");
const path = require("path");
const sharp = require("C:/Users/dayan/AppData/Local/Temp/imgtools/node_modules/sharp");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "assets", "src");
const OUT = path.join(ROOT, "assets", "img");
const CATALOG = path.join(ROOT, "catalog.json");

const SIZES = {
  thumb: 520,
  large: 1100,
};
const QUALITY = 80;

function ensureDir(d) {
  fs.mkdirSync(d, { recursive: true });
}

async function main() {
  ensureDir(path.join(OUT, "thumb"));
  ensureDir(path.join(OUT, "large"));

  const data = JSON.parse(fs.readFileSync(CATALOG, "utf8"));

  let ok = 0;
  let fail = 0;
  const errors = [];

  for (const p of data.products) {
    const imgs = [];
    const list = p.images || [];
    for (let i = 0; i < list.length; i++) {
      const rel = list[i];
      const srcPath = path.join(SRC, rel);
      if (!fs.existsSync(srcPath)) {
        errors.push("AUSENTE: " + rel);
        fail++;
        continue;
      }
      const name = `${p.slug}-${i + 1}.webp`;
      const entry = { src: rel.replace(/\\/g, "/") };
      try {
        for (const [kind, width] of Object.entries(SIZES)) {
          const outPath = path.join(OUT, kind, name);
          const info = await sharp(srcPath)
            .rotate()
            .resize({ width, withoutEnlargement: true })
            .webp({ quality: QUALITY })
            .toFile(outPath);
          entry[kind] = `assets/img/${kind}/${name}`;
          entry[`${kind}_w`] = info.width;
          entry[`${kind}_h`] = info.height;
        }
        imgs.push(entry);
        ok++;
      } catch (e) {
        errors.push(`${rel}: ${e.message}`);
        fail++;
      }
    }
    p.img = imgs;
  }

  fs.writeFileSync(CATALOG, JSON.stringify(data, null, 2), "utf8");

  console.log("Imagens otimizadas:", ok, "| falhas:", fail);
  if (errors.length) {
    console.log("--- erros ---");
    for (const e of errors.slice(0, 30)) console.log("  " + e);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
