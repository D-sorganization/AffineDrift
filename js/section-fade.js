/**
 * Section scroll-reveal fades for non-article pages (#5164: skipped on articles for CLS).
 */

function revealAllSections(sections) {
    for (const section of sections) {
        section.style.opacity = "1";
        section.style.transform = "none";
        section.style.visibility = "visible";
        section.style.transition = "";
    }
}

export function initFadeAnimations() {
    const allSections = document.getElementsByTagName("section");
    const quartoContent = document.getElementById("quarto-content");
    if (quartoContent?.classList.contains("page-layout-article")) {
        revealAllSections(allSections);
        return;
    }

    const isMobile = window.innerWidth <= 768;
    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (!isMobile && !prefersReducedMotion) {
        const observer = new IntersectionObserver((entries) => {
            for (const entry of entries) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = "1";
                    observer.unobserve(entry.target);
                }
            }
        }, { threshold: 0, rootMargin: "0px" });

        const animationStates = [];
        for (const section of allSections) {
            if (
                !section.classList.contains("page-header") &&
                !section.classList.contains("article-section")
            ) {
                animationStates.push({
                    section,
                    top: section.getBoundingClientRect().top,
                });
            }
        }

        const windowHeight = window.innerHeight;
        for (const { section, top } of animationStates) {
            if (top > windowHeight) {
                section.style.opacity = "0";
                section.style.transition = "opacity 0.4s ease";
                observer.observe(section);
            } else {
                section.style.opacity = "1";
            }
        }
        return;
    }

    revealAllSections(allSections);
}
