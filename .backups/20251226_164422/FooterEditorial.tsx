import { useTranslation } from "react-i18next";

import RevealOnScroll from './RevealOnScroll';
import logo from '@/assets/logo-udc.png';

const FooterEditorial = () => {
  const { t } = useTranslation();

  return (
    <footer id="contact" className="section-spacing border-t border-border" role="contentinfo">
      <div className="editorial-container">
        <RevealOnScroll>
          <span className="label-text block mb-12">{t("footer.getInTouch")}</span>
        </RevealOnScroll>

        <RevealOnScroll delay={0.2}>
          <h2 className="section-heading text-foreground mb-16">
            Let's build something
            <span className="text-primary italic"> meaningful</span>
          </h2>
        </RevealOnScroll>

        <RevealOnScroll delay={0.3}>
          <a 
            href="mailto:mike@uniteddutchcompany.com" 
            className="inline-block font-serif text-3xl md:text-4xl text-primary hover:text-foreground transition-colors duration-500 mb-24"
          >
            mike@uniteddutchcompany.com
          </a>
        </RevealOnScroll>

        <RevealOnScroll delay={0.4}>
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-12 pt-24 border-t border-border">
            <div>
              <img 
                src={logo} 
                alt={t("footer.unitedDutchCompany")} 
                className="h-12 w-auto mb-6 opacity-60"
              />
              <p className="text-muted-foreground text-sm">
                Amsterdam, Netherlands
              </p>
            </div>

            <div className="flex flex-col md:flex-row gap-8 md:gap-16">
              <a 
                href="#" 
                className="label-text text-muted-foreground hover:text-primary transition-colors duration-300"
              >
                LinkedIn
              </a>
              <a 
                href="#" 
                className="label-text text-muted-foreground hover:text-primary transition-colors duration-300"
              >
                Twitter
              </a>
            </div>

            <p className="text-muted-foreground text-sm">
              © 2024 United Dutch Company
            </p>
          </div>
        </RevealOnScroll>
      </div>
    </footer>
  );
};

export default FooterEditorial;
