# PipelineForge

İngilizce sürüm: [README.md](README.md)

Forge ailesinin standart **Pipeline DAG** şemaları için üretici. Küçük bir proje-spec'ini alıp
kendi kendine yeten, çift dilli (`tr`/`en`) bir HTML sayfasına çevirir: nokta-ızgara canvas üzerinde
elle-çizilmiş inline-SVG node-graph, tiplenmiş kartlar (kod çipi + ad + araç + portlar), eğri bezier
oklar, karar düğümü, modül matrisi tablosu ve izole ortam listesi. Her proje **aynı tornadan** çıkar;
yalnız graf içeriği ile kategori paleti değişir.

Amaç: RNAForge, VirusForge ve BacForge'un `docs/pipeline_architecture.html`'leri elle çizilmişti.
PipelineForge bunu tekrarlanabilir kılar — tek iskelet, tek komut, spec'le beslenir.

## Nasıl çalışır

- **İskelet sabit** (RNAForge referansı): CSS/tema token'ları, bölümler, düğüm dili, TR/EN toggle ve
  yerleşim mekaniği `pipelineforge/forge.py` içinde. Görünüm için tek kaynak-doğruluk.
- **İçerik spec'ten** (`specs/<proje>.yml`): düğümler, kenarlar, kategoriler, araçlar, ortamlar, karar.
- **Kenarlar gerçek `run()` bağımlılıkları.** Spec yazarı bunları projenin kodundan çıkarır
  (`state.is_done` / `inputs()` guard'ları) — şema pipeline'ın gerçekte nasıl koştuğuyla örtüşür.
- **Renkler rol, kategoriler projeye özgü.** Mavi = ortak (ailede sabit), yeşil ve amber = iki dal
  kategorisi, mor = tanı. Her proje kendi kategorisini (organizma, molekül, platform, …) bu rollere oturtur.
- **Yerleşim motoru.** Her düğüm bir `lane` (x-kolonu) ve `y` bildirir; motor piksel konumlarını
  hesaplar ve her kenarı tiplenmiş portlar (`top`/`bottom`/`left`/`right`) arasında bezier olarak,
  kart kenarına dik girip çıkacak şekilde çizer. Hub yelpazeleri `to_port: left` kullanır.

## Kullanım

```bash
pip install -e .            # ya da: pip install pyyaml
pipelineforge render specs/rnaforge.yml -o ../rnaforge-pipeline/docs/pipeline_architecture.html
```

Her render kendini doğrular: sayfa başına düğüm/kenar sayısını basar, etiket dengesini ve bozuk
karakter (`U+FFFD`) olmadığını kontrol eder. Çıktıyı GitHub Pages'te yayımla (`Settings → Pages →
main /docs`) ki proje README'sindeki rozet canlı render'lı sayfaya bağlansın.

## Örnek spec'ler

| Spec | Proje | Arketip | Düğüm / kenar |
|---|---|---|---|
| `specs/rnaforge.yml`   | RNAForge   | hub-and-spoke (m06) | 21 / 23 |
| `specs/virusforge.yml` | VirusForge | molekül-dal (DNA/RNA) | 13 / 16 |
| `specs/bacforge.yml`   | BacForge   | hub-and-spoke (M04) | 19 / 20 |

## Yeni proje ekleme

1. Projenin modül kodundan gerçek `run()` bağımlılıklarını çıkar (hangi modül hangisini şart koşuyor).
2. `specs/<proje>.yml` yaz: `meta`, `lanes`, `categories`, `nodes` (kod, tr/en ad, araç, `cat`,
   `lane`, `y`, `dep`), `edges`, `envs`, opsiyonel `decision` ve `hub_label`.
3. `pipelineforge render specs/<proje>.yml -o <proje>/docs/pipeline_architecture.html`.
4. Commit et, Pages'i aç, proje README'sindeki diyagram rozetini render'lı URL'e bağla.
