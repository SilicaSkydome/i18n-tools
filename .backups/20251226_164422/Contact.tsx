import { useState, useRef } from 'react';
import { useTranslation } from "react-i18next";
import { motion, useInView } from 'framer-motion';
import { Send, MapPin, Mail, Phone } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import PageLayout from '@/components/PageLayout';
import ScrollReactiveBackground from '@/components/ScrollReactiveBackground';

const Contact = () => {
  const { t } = useTranslation();

  const { toast } = useToast();
  const heroRef = useRef(null);
  const formRef = useRef(null);

  const heroInView = useInView(heroRef, { once: true });
  const formInView = useInView(formRef, { once: true, margin: "-80px" });

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const payload = {
        name: formData.name,
        email: formData.email,
        company: formData.company,
        message: formData.message,
        timestamp: new Date().toISOString(),
        source: 'website',
      };
      
      console.log('Submitting form:', payload);
      
      // Submit to n8n webhook via API proxy
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('Response status:', response.status);
      console.log('Response:', response);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error('Failed to send message');
      }

      toast({
        title: t('contact.form.success'),
        description: "We'll respond within 24 hours.",
      });
      
      setFormData({ name: '', email: '', company: '', message: '' });
    } catch (error) {
      console.error('Form submission error:', error);
      toast({
        title: t('contact.form.error'),
        description: "Please try again or email us directly.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageLayout 
      title="Contact" 
      description="Get in touch with United Dutch Company. Let's discuss your next AI-driven project and explore how we can transform your enterprise operations."
    >
      <ScrollReactiveBackground />
      
      {/* Hero */}
      <section ref={heroRef} className="pt-40 pb-28 relative">
        <div className="container-full">
          <motion.span
            className="label-caps block mb-8"
            initial={{ opacity: 0, y: 40 }}
            animate={heroInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
            {t('nav.contacts')}
          </motion.span>
          <div className="overflow-hidden pb-4">
            <motion.h1
              className="heading-hero max-w-5xl"
              initial={{ y: 100 }}
              animate={heroInView ? { y: 0 } : {}}
              transition={{ duration: 1, delay: 0.1, ease: [0.25, 0.1, 0.25, 1] }}
            >
              {t('contact.hero.title')}{' '}
              <span className="font-editorial text-primary">{t('contact.hero.titleHighlight')}</span>
            </motion.h1>
          </div>
          <motion.p
            className="text-body max-w-2xl mt-12"
            initial={{ opacity: 0, x: -50 }}
            animate={heroInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            {t('contact.hero.description')}
          </motion.p>
        </div>
      </section>

      {/* Contact Form & Info */}
      <section ref={formRef} className="section-padding border-t-2 border-border">
        <div className="container-full">
          <div className="grid lg:grid-cols-2 gap-20 lg:gap-32">
            {/* Form */}
            <motion.form
              onSubmit={handleSubmit}
              className="space-y-10 will-change-transform"
              initial={{ opacity: 0, x: -50 }}
              animate={formInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.7, ease: "easeOut" }}
            >
              <div className="grid md:grid-cols-2 gap-10">
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={formInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.6, delay: 0.1 }}
                >
                  <label className="label-caps text-foreground/50 block mb-4">{t('contact.form.name')}</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-0 py-5 bg-transparent border-b-2 border-border focus:border-primary outline-none transition-colors duration-300 text-foreground text-lg"
                    placeholder={t("contact.yourName")}
                  />
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={formInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <label className="label-caps text-foreground/50 block mb-4">{t('contact.form.email')}</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-0 py-5 bg-transparent border-b-2 border-border focus:border-primary outline-none transition-colors duration-300 text-foreground text-lg"
                    placeholder={t('contact.form.emailPlaceholder')}
                  />
                </motion.div>
              </div>

              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={formInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <label className="label-caps text-foreground/50 block mb-4">{t('contact.form.company')}</label>
                <input
                  type="text"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  className="w-full px-0 py-5 bg-transparent border-b-2 border-border focus:border-primary outline-none transition-colors duration-300 text-foreground text-lg"
                  placeholder={t('contact.form.companyPlaceholder')}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={formInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <label className="label-caps text-foreground/50 block mb-4">{t('contact.form.message')}</label>
                <textarea
                  required
                  rows={4}
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  className="w-full px-0 py-5 bg-transparent border-b-2 border-border focus:border-primary outline-none transition-colors duration-300 text-foreground resize-none text-lg"
                  placeholder={t("contact.tellUsAboutYourProject")}
                />
              </motion.div>

              <motion.button
                type="submit"
                disabled={isSubmitting}
                className="group relative inline-flex items-center gap-3 px-10 py-4 bg-primary text-primary-foreground font-medium overflow-hidden mt-6 disabled:opacity-50"
                initial={{ opacity: 0, y: 30 }}
                animate={formInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.5 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {/* Animated background sweep */}
                <motion.span
                  className="absolute inset-0 bg-primary-foreground/10"
                  initial={{ x: '-100%' }}
                  whileHover={{ x: '100%' }}
                  transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                />
                
                <span className="relative z-10">
                  {isSubmitting ? t('contact.form.sending') : t('contact.form.submit')}
                </span>
                
                {!isSubmitting && (
                  <motion.span
                    className="relative z-10"
                    initial={{ x: 0, y: 0 }}
                    whileHover={{ x: 3, y: -3 }}
                    transition={{ duration: 0.3, ease: 'easeOut' }}
                  >
                    <Send className="w-4 h-4" />
                  </motion.span>
                )}
              </motion.button>
            </motion.form>

            {/* Contact Info */}
            <motion.div
              className="space-y-14 will-change-transform"
              initial={{ opacity: 0, x: 50 }}
              animate={formInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.15, ease: "easeOut" }}
            >
              <div>
                <h3 className="text-2xl text-foreground mb-10">{t("contact.contactInformation")}</h3>
                <div className="space-y-8">
                  <motion.div 
                    className="flex items-start gap-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={formInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5, delay: 0.3 }}
                  >
                    <MapPin className="w-5 h-5 text-primary mt-1.5 shrink-0" />
                    <div>
                      <div className="text-base text-foreground mb-2">{t('contact.headquarters')}</div>
                      <a 
                        href="https://maps.app.goo.gl/xSkms2r9d4uXRYaQ7" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-small text-lg hover:text-primary transition-colors block"
                      >
                        Strada București 67, MD-2012<br />
                        Chișinău, Moldova
                      </a>
                    </div>
                  </motion.div>
                  <motion.div 
                    className="flex items-start gap-6"
                    initial={{ opacity: 0, x: 30 }}
                    animate={formInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.5, delay: 0.4 }}
                  >
                    <Mail className="w-5 h-5 text-primary mt-1.5 shrink-0" />
                    <div>
                      <div className="text-base text-foreground mb-2">{t('contact.form.email')}</div>
                      <a href="mailto:mike@uniteddutchcompany.com" className="text-small text-lg hover:text-primary transition-colors">
                        mike@uniteddutchcompany.com
                      </a>
                    </div>
                  </motion.div>
                  <motion.div 
                    className="flex items-start gap-6"
                    initial={{ opacity: 0, y: -20 }}
                    animate={formInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5, delay: 0.5 }}
                  >
                    <Phone className="w-5 h-5 text-primary mt-1.5 shrink-0" />
                    <div>
                      <div className="text-base text-foreground mb-2">{t('contact.phone')}</div>
                      <a href="tel:+37361150777" className="text-small text-lg hover:text-primary transition-colors">
                        +373 611 50 777
                      </a>
                    </div>
                  </motion.div>
                </div>
              </div>

              <motion.div 
                className="pt-10 border-t-2 border-border"
                initial={{ opacity: 0, x: 40 }}
                animate={formInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.6 }}
              >
                <h4 className="text-xl text-foreground mb-4">{t("contact.enterpriseInquiries")}</h4>
                <p className="text-small text-lg mb-5">
                  {t('contact.enterpriseDescription')}
                </p>
                <a href="mailto:mike@uniteddutchcompany.com" className="text-base text-primary hover:underline">
                  mike@uniteddutchcompany.com
                </a>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>
    </PageLayout>
  );
};

export default Contact;