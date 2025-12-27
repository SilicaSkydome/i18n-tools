import { Link } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import { useTranslation } from "react-i18next";
import logo from '@/assets/logo-udc.png';

const Footer = () => {
  const { t } = useTranslation();

  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  const links = {
    company: [
      { label: 'About', path: '/about' },
      { label: 'Projects', path: '/projects' },
      { label: 'Partners', path: '/partners' },
      { label: 'Contacts', path: '/contact' },
    ],
    capabilities: [
      { label: 'AI Systems', path: '/capabilities/ai-systems' },
      { label: 'Technology Platforms', path: '/capabilities/technology-platforms' },
      { label: 'Applied Research', path: '/capabilities/applied-research' },
      { label: 'Strategic Partnerships', path: '/capabilities/strategic-partnerships' },
    ],
  };

  return (
    <footer ref={ref} className="py-20 md:py-28 bg-background relative z-10">
      <motion.div 
        className="container-full"
        initial={{ opacity: 0 }}
        animate={isInView ? { opacity: 1 } : {}}
        transition={{ duration: 0.8 }}
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-12 mb-20">
          {/* Brand */}
          <div className="lg:col-span-2">
            <motion.div
              className="flex items-center gap-3 mb-6"
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <img 
                src={logo} 
                alt="UDC" 
                className="h-10 w-auto opacity-70"
              />
              <span className="font-sans font-bold text-lg tracking-wide uppercase text-[#ffed85]/70">
                United Dutch Company
              </span>
            </motion.div>
            <p className="text-small max-w-sm">
              AI-driven technology solutions built for scale, 
              security, and real-world impact.
            </p>
          </div>

          {/* Company */}
          <div>
            <h4 className="label-caps text-foreground/60 mb-6">Company</h4>
            <ul className="space-y-4">
              {links.company.map((link, index) => (
                <motion.li 
                  key={link.path}
                  initial={{ opacity: 0, x: -10 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.05 }}
                >
                  <Link
                    to={link.path}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors duration-300"
                  >
                    {link.label}
                  </Link>
                </motion.li>
              ))}
            </ul>
          </div>

          {/* Capabilities */}
          <div>
            <h4 className="label-caps text-foreground/60 mb-6">Capabilities</h4>
            <ul className="space-y-4">
              {links.capabilities.map((link, index) => (
                <motion.li 
                  key={link.label}
                  initial={{ opacity: 0, x: -10 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.4, delay: 0.4 + index * 0.05 }}
                >
                  <Link
                    to={link.path}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors duration-300"
                  >
                    {link.label}
                  </Link>
                </motion.li>
              ))}
            </ul>
          </div>

          {/* Contact Details */}
          <div>
            <h4 className="label-caps text-foreground/60 mb-6">Contact</h4>
            <ul className="space-y-4">
              <motion.li
                initial={{ opacity: 0, x: -10 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.4, delay: 0.5 }}
              >
                <a 
                  href="mailto:mike@uniteddutchcompany.com"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors duration-300"
                >
                  mike@uniteddutchcompany.com
                </a>
              </motion.li>
              <motion.li
                initial={{ opacity: 0, x: -10 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.4, delay: 0.55 }}
              >
                <a 
                  href="tel:+37361150777"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors duration-300"
                >
                  +373 611 50 777
                </a>
              </motion.li>
              <motion.li
                initial={{ opacity: 0, x: -10 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.4, delay: 0.6 }}
                className="text-sm text-muted-foreground"
              >
                <a 
                  href="https://maps.app.goo.gl/xSkms2r9d4uXRYaQ7" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  <span>{t("footer.stradaBucureti67Md2012")}</span>
                  <br />
                  <span>{t("footer.chiinuMoldova")}</span>
                </a>
              </motion.li>
              <motion.li
                initial={{ opacity: 0, x: -10 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.4, delay: 0.65 }}
                className="text-xs text-muted-foreground/70 pt-2"
              >
                <span>{t("footer.unitedDutchCompanySrl")}</span>
                <br />
                <span>IDNO: 1025600039710</span>
              </motion.li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <motion.div 
          className="pt-10 border-t border-border flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <p className="text-xs text-muted-foreground">
            © 2024 United Dutch Company. All rights reserved.
          </p>
          <div className="flex gap-8">
            <Link to="/privacy" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              Privacy Policy
            </Link>
            <Link to="/terms" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              Terms
            </Link>
            <a href="https://www.linkedin.com/company/united-dutch-company/" target="_blank" rel="noopener noreferrer" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              LinkedIn
            </a>
          </div>
        </motion.div>
      </motion.div>
    </footer>
  );
};

export default Footer;
