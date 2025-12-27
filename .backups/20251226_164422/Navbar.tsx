import { useState } from 'react';
import { useTranslation } from "react-i18next";
import { Menu, X } from 'lucide-react';
import logo from '@/assets/logo-udc.png';

const Navbar = () => {
  const { t } = useTranslation();

  const [isOpen, setIsOpen] = useState(false);

  const navItems = ['Home', 'About', 'Solutions', 'Projects', 'Partners', 'Contact'];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-xl border-b border-border/50">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <a href="#" className="flex items-center gap-3 group">
            <img 
              src={logo} 
              alt={t("nav.unitedDutchCompany")} 
              className="h-10 w-auto group-hover:drop-shadow-[0_0_10px_hsl(40,95%,55%,0.5)] transition-all duration-300"
            />
            <span className="font-mono font-bold text-sm tracking-tight hidden sm:block">
              <span className="text-primary">UNITED</span>
              <span className="text-foreground"> DUTCH</span>
              <span className="text-foreground"> COMPANY</span>
            </span>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors duration-300 relative group"
              >
                {item}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300" />
              </a>
            ))}
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <button className="px-6 py-2.5 bg-primary text-primary-foreground font-mono font-bold text-sm rounded-lg hover:glow-gold transition-all duration-300 hover:scale-105">
              {t("nav.getStarted")}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-foreground p-2"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t border-border/50">
            <div className="flex flex-col gap-4">
              {navItems.map((item) => (
                <a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors py-2"
                  onClick={() => setIsOpen(false)}
                >
                  {item}
                </a>
              ))}
              <button className="mt-4 px-6 py-3 bg-primary text-primary-foreground font-mono font-bold text-sm rounded-lg">
                {t("nav.getStarted")}
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
