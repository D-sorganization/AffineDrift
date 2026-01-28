/**
 * AffineDrift - SEO Enhancements
 * Handles dynamic SEO features including:
 * - Article-specific structured data injection
 * - Lazy loading for images
 * - Related articles suggestions
 */

(function () {
  "use strict";

  /**
   * Inject Article schema.org structured data for article pages
   */
  function injectArticleSchema() {
    // Only inject on article pages
    const path = window.location.pathname;
    if (!path.includes("/articles/")) return;

    // Get page metadata
    const title =
      document.querySelector("title")?.textContent ||
      document.querySelector("h1")?.textContent ||
      "Untitled Article";
    const description =
      document.querySelector('meta[name="description"]')?.content ||
      document.querySelector(".abstract p")?.textContent ||
      "";
    const canonical =
      document.querySelector('link[rel="canonical"]')?.href ||
      window.location.href;

    // Check if schema already exists
    if (document.querySelector('script[type="application/ld+json"]')) {
      return;
    }

    const schema = {
      "@context": "https://schema.org",
      "@type": "ScholarlyArticle",
      headline: title.substring(0, 110),
      description: description.substring(0, 160),
      author: {
        "@type": "Person",
        name: "Dieter Olson",
        url: "https://affinedrift.com/about.html",
      },
      publisher: {
        "@type": "Organization",
        name: "AffineDrift",
        logo: {
          "@type": "ImageObject",
          url: "https://affinedrift.com/logo/logo_transparent_1.png",
        },
      },
      mainEntityOfPage: {
        "@type": "WebPage",
        "@id": canonical,
      },
      datePublished: "2024-01-01",
      dateModified: new Date().toISOString().split("T")[0],
      inLanguage: "en",
      isAccessibleForFree: true,
      keywords:
        "golf biomechanics, control theory, affine systems, robotics, multibody dynamics",
      about: [
        { "@type": "Thing", name: "Golf Swing Biomechanics" },
        { "@type": "Thing", name: "Control-Affine Systems" },
        { "@type": "Thing", name: "Multibody Dynamics" },
      ],
    };

    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  }

  /**
   * Add lazy loading to images that don't have it
   */
  function enableLazyLoading() {
    // Add loading="lazy" to images without it
    document.querySelectorAll("img:not([loading])").forEach((img) => {
      // Don't lazy load images above the fold
      const rect = img.getBoundingClientRect();
      if (rect.top > window.innerHeight) {
        img.loading = "lazy";
        img.decoding = "async";
      }
    });

    // Add lazy loading to iframes (embeds)
    document.querySelectorAll("iframe:not([loading])").forEach((iframe) => {
      iframe.loading = "lazy";
    });
  }

  /**
   * Add missing alt text to images (with placeholder)
   */
  function fixMissingAltText() {
    document.querySelectorAll("img:not([alt]), img[alt='']").forEach((img) => {
      // Try to derive alt from filename or context
      const src = img.src || "";
      const filename = src.split("/").pop()?.split(".")[0] || "";
      const altText = filename
        .replace(/[-_]/g, " ")
        .replace(/\b\w/g, (l) => l.toUpperCase());
      img.alt = altText || "Image";
    });
  }

  /**
   * Generate related articles section based on concepts
   */
  async function generateRelatedArticles() {
    // Only on article pages
    const path = window.location.pathname;
    if (!path.includes("/articles/")) return;

    // Check if related articles container exists
    const container = document.getElementById("related-articles");
    if (!container) return;

    try {
      // Load search index
      const response = await fetch("/data/search_index.json");
      if (!response.ok) return;

      const data = await response.json();
      const currentUrl = path;

      // Find current article
      const current = data.entries.find((e) => e.url === currentUrl);
      if (!current || !current.concepts) return;

      // Score other articles by concept overlap
      const scored = data.entries
        .filter((e) => e.url !== currentUrl && e.type === "article")
        .map((e) => {
          const overlap = (e.concepts || []).filter((c) =>
            current.concepts.includes(c)
          ).length;
          return { ...e, score: overlap };
        })
        .filter((e) => e.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 3);

      if (scored.length === 0) return;

      // Render related articles
      const html = `
        <h3>Related Articles</h3>
        <div class="related-articles-list">
          ${scored
            .map(
              (article) => `
            <a href="${article.url}" class="related-article">
              <span class="related-title">${article.title}</span>
              ${article.description ? `<span class="related-desc">${article.description.substring(0, 80)}...</span>` : ""}
            </a>
          `
            )
            .join("")}
        </div>
      `;

      container.innerHTML = html;
    } catch (error) {
      console.warn("Could not load related articles:", error);
    }
  }

  /**
   * Add breadcrumb schema
   */
  function injectBreadcrumbSchema() {
    const path = window.location.pathname;
    const parts = path.split("/").filter(Boolean);

    if (parts.length < 2) return;

    const breadcrumbs = [
      { name: "Home", url: "https://affinedrift.com/" },
    ];

    let currentPath = "";
    parts.forEach((part, index) => {
      currentPath += "/" + part;
      const name = part
        .replace(".html", "")
        .replace(/-/g, " ")
        .replace(/\b\w/g, (l) => l.toUpperCase());
      breadcrumbs.push({
        name: name,
        url: "https://affinedrift.com" + currentPath,
      });
    });

    const schema = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: breadcrumbs.map((item, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: item.name,
        item: item.url,
      })),
    };

    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  }

  /**
   * Initialize all SEO enhancements
   */
  function init() {
    injectArticleSchema();
    injectBreadcrumbSchema();
    enableLazyLoading();
    fixMissingAltText();

    // Delay non-critical tasks
    if ("requestIdleCallback" in window) {
      requestIdleCallback(generateRelatedArticles);
    } else {
      setTimeout(generateRelatedArticles, 1000);
    }
  }

  // Run on DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Expose for external use
  window.AffineDriftSEO = {
    injectArticleSchema,
    generateRelatedArticles,
    enableLazyLoading,
  };
})();
