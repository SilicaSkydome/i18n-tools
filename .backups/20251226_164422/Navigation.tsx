import { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion';
import { Menu, X, ChevronDown } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import logo from '@/assets/logo-udc.png';

const Navigation = () => {
  const { t, i18n } = useTranslation();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isLangOpen, setIsLangOpen] = useState(false);
  const location = useLocation();
  
  const navItems = [{
    label: t('nav.home'),
    path: '/'
  }, {
    label: t('nav.about'),
    path: '/about'
  }, {
    label: t('nav.projects'),
    path: '/projects'
  }, {
    label: t('nav.partners'),
    path: '/partners'
  }, {
    label: t('nav.contacts'),
    path: '/contact'
  }];
  
  const languages = [
    { code: 'en', label: 'EN', name: 'English' },
    { code: 'nl', label: 'NL', name: 'Nederlands' },
    { code: 'de', label: 'DE', name: 'Deutsch' },
    { code: 'ro', label: 'RO', name: 'Română' },
    { code: 'el', label: 'EL', name: 'Ελληνικά' },
    { code: 'ru', label: 'RU', name: 'Русский' }
  ];
  
  const currentLang = languages.find(lang => lang.code === i18n.language)?.label || 'EN';
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  useEffect(() => {
    setIsMobileOpen(false);
  }, [location]);
  return <>
      {/* Skip to main content link for keyboard navigation */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:bg-primary focus:text-primary-foreground focus:px-6 focus:py-3 focus:rounded focus:font-medium focus:shadow-lg"
      >
        Skip to main content
      </a>
      
      <motion.header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-700 ${isScrolled ? 'bg-background/80 backdrop-blur-xl' : ''}`} initial={{
      y: -100,
      opacity: 0
    }} animate={{
      y: 0,
      opacity: 1
    }} transition={{
      duration: 1,
      ease: [0.16, 1, 0.3, 1]
    }}>
        <nav className="container-full" role="navigation" aria-label="Main navigation">
          <div className="flex items-center justify-between h-20 md:h-24">
            <Link to="/" className="relative z-50 flex items-center gap-3" aria-label="United Dutch Company - Home">
              <motion.img src={logo} alt="UDC" className="h-10 md:h-12 w-auto" whileHover={{
              opacity: 0.7
            }} transition={{
              duration: 0.3
            }} />
              <span className="font-sans font-bold text-lg md:text-xl tracking-wide hidden sm:block uppercase text-[#ffed85]">
                UNITED DUTCH COMPANY
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center gap-12">
              {navItems.map(item => <NavLink key={item.path} to={item.path} isActive={location.pathname === item.path}>
                  {item.label}
                </NavLink>)}

              {/* Language Switcher */}
              <div className="relative ml-4">
                <button 
                  onClick={() => setIsLangOpen(!isLangOpen)} 
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors duration-300"
                  aria-label="Select language"
                  aria-expanded={isLangOpen}
                  aria-haspopup="true"
                >
                  <span className="tracking-widest">{currentLang}</span>
                  <ChevronDown className={`w-3 h-3 transition-transform duration-300 ${isLangOpen ? 'rotate-180' : ''}`} />
                </button>

                <AnimatePresence>
                  {isLangOpen && <motion.div className="absolute top-full right-0 mt-4 py-3 bg-background border border-border min-w-[80px] z-50 shadow-lg" initial={{
                  opacity: 0,
                  y: -10
                }} animate={{
                  opacity: 1,
                  y: 0
                }} exit={{
                  opacity: 0,
                  y: -10
                }} transition={{
                  duration: 0.25,
                  ease: [0.16, 1, 0.3, 1]
                }}>
                      {languages.map(lang => <button key={lang.code} onClick={() => {
                    i18n.changeLanguage(lang.code);
                    setIsLangOpen(false);
                  }} className={`block w-full px-4 py-2 text-left text-xs tracking-widest transition-colors duration-200 ${i18n.language === lang.code ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`}>
                          {lang.label}
                        </button>)}
                    </motion.div>}
                </AnimatePresence>
              </div>
            </div>

            {/* Mobile Toggle */}
            <button 
              onClick={() => setIsMobileOpen(!isMobileOpen)} 
              className="lg:hidden relative z-50 p-2 -mr-2"
              aria-label={isMobileOpen ? "Close menu" : "Open menu"}
              aria-expanded={isMobileOpen}
            >
              <motion.div animate={{
              rotate: isMobileOpen ? 90 : 0
            }} transition={{
              duration: 0.3
            }}>
                {isMobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </motion.div>
            </button>
          </div>
        </nav>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileOpen && <motion.div className="fixed inset-0 z-40 bg-background lg:hidden" initial={{
        opacity: 0
      }} animate={{
        opacity: 1
      }} exit={{
        opacity: 0
      }} transition={{
        duration: 0.4
      }}>
            <div className="flex flex-col justify-center h-full px-10">
              {navItems.map((item, index) => <motion.div key={item.path} initial={{
            opacity: 0,
            x: -30
          }} animate={{
            opacity: 1,
            x: 0
          }} transition={{
            delay: index * 0.1,
            duration: 0.5,
            ease: [0.16, 1, 0.3, 1]
          }} className="border-b border-border py-6">
                  <Link to={item.path} className={`text-3xl font-light tracking-tight ${location.pathname === item.path ? 'text-primary' : 'text-foreground'}`}>
                    {item.label}
                  </Link>
                </motion.div>)}
              <motion.div initial={{
            opacity: 0
          }} animate={{
            opacity: 1
          }} transition={{
            delay: 0.5
          }} className="flex gap-6 mt-10">
                {languages.map(lang => <button key={lang.code} onClick={() => i18n.changeLanguage(lang.code)} className={`text-sm tracking-widest ${i18n.language === lang.code ? 'text-primary' : 'text-muted-foreground'}`}>
                    {lang.label}
                  </button>)}
              </motion.div>
            </div>
          </motion.div>}
      </AnimatePresence>
    </>;
};

// Animated Nav Link with underline
const NavLink = ({
  to,
  isActive,
  children
}: {
  to: string;
  isActive: boolean;
  children: React.ReactNode;
}) => {
  return <Link to={to} className="relative group py-2">
      <span className={`text-sm transition-colors duration-300 ${isActive ? 'text-foreground' : 'text-muted-foreground group-hover:text-foreground'}`}>
        {children}
      </span>
      <motion.span className="absolute bottom-0 left-0 h-px bg-primary" initial={{
      width: isActive ? '100%' : '0%'
    }} animate={{
      width: isActive ? '100%' : '0%'
    }} whileHover={{
      width: '100%'
    }} transition={{
      duration: 0.3,
      ease: [0.16, 1, 0.3, 1]
    }} />
    </Link>;
};
export default Navigation;