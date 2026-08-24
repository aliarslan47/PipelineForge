# PipelineForge

Forge ailesinin standart **Pipeline DAG** diyagramları için bir üretici — proje başına küçük bir spec'i, kendine yeten, çift dilli (`tr`/`en`) bir HTML düğüm grafiğine dönüştürür.

[![Pipeline DAG](https://img.shields.io/badge/output-Pipeline%20DAG-0d6b8f)](https://github.com/aliarslan47/PipelineForge)
[![family](https://img.shields.io/badge/family-Forge-2f8f5b)](https://github.com/aliarslan47/PipelineForge)
[![spec](https://img.shields.io/badge/driven%20by-YAML%20spec-c07211)](https://github.com/aliarslan47/PipelineForge)

**Türkçe** · [English](README.md)

## Nedir?

PipelineForge, Forge ailesinin diyagram-üretici üyesidir — BacForge, VirusForge ve RNAForge ile aynı görsel standart, ancak pipeline değil bir araç. Her projenin `docs/pipeline_architecture.html`'i aynı kalıptan çıkar; yalnızca grafik içeriği ve kategori paleti değişir.

## Ne yapar?

Bir YAML spec'inden, noktalı bir tuval üzerine elle-çizilmiş inline-SVG bir düğüm grafiği render eder: tipli kartlar (kod çipi + ad + araç + portlar), eğri bezier kenarlar, bir karar baklavası, bir modül matris tablosu, izole-ortam listesi ve bir TR/EN geçişi.

- **İskelet sabittir** (RNAForge referansı): CSS/tema, bölümler, düğüm sözlüğü ve yerleşim mekaniği `pipelineforge/forge.py` içindedir — görünüm için tek doğruluk kaynağı.
- **İçerik spec'ten gelir** (`specs/<proje>.yml`): düğümler, kenarlar, kategoriler, araçlar, ortamlar, karar düğümü.
- **Kenarlar gerçek `run()` bağımlılıklarıdır**; projenin kodundan çıkarılır, böylece diyagram pipeline'ın gerçekte nasıl çalıştığıyla örtüşür — üstünkörü bir eskiz değil.
- **Renkler roldür, kategoriler proje-bazlıdır**: mavi = ortak, yeşil/kehribar = dallar, mor = tanısal. Her render kendini doğrular (düğüm/kenar sayısı, etiket dengesi, `U+FFFD` yok).

## Kurulum

```bash
git clone https://github.com/aliarslan47/PipelineForge.git
cd PipelineForge

pip install -e .            # ya da: pip install pyyaml
```

## Kullanım

```bash
pipelineforge render specs/rnaforge.yml   -o ../rnaforge-pipeline/docs/pipeline_architecture.html
pipelineforge render specs/virusforge.yml -o ../VirusForge/docs/pipeline_architecture.html
pipelineforge render specs/bacforge.yml   -o ../BacForge/docs/pipeline_architecture.html
```

Çıktıyı GitHub Pages'te yayınla (`Settings → Pages → main /docs`); böylece proje README'sindeki diyagram rozeti canlı bir sayfaya bağlanır.

## Modüller

Render ettiği spec'ler (her Forge projesi için bir tane); yeni proje eklemek için projenin gerçek `run()` bağımlılıklarını `specs/<proje>.yml`'ye çıkar, render et ve README rozetini yayınlanan sayfaya yönlendir.

| Spec | Proje | Arketip | Düğüm / kenar |
|---|---|---|---|
| `specs/rnaforge.yml` | RNAForge | hub-and-spoke (m06) | 21 / 23 |
| `specs/virusforge.yml` | VirusForge | molekül dalı (DNA/RNA) | 13 / 16 |
| `specs/bacforge.yml` | BacForge | hub-and-spoke (M04) | 19 / 20 |

Tam spec formatı ve "yeni proje ekleme" adımları kaynak kod ile `specs/` içindedir.

---

Forge ailesi: **PipelineForge** (DAG üreticisi) · [RNAForge](https://github.com/aliarslan47/RNAForge) (bulk RNA-seq) · [BacForge](https://github.com/aliarslan47/BacForge) (bakteri) · [VirusForge](https://github.com/aliarslan47/VirusForge) (virüs/faj).
