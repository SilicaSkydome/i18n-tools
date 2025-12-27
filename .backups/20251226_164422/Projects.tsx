import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { useRef, useState, useEffect } from 'react';
import { useTranslation } from "react-i18next";
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Activity, BarChart3, Cpu, Languages } from 'lucide-react';
import PageLayout from '@/components/PageLayout';
import ScrollReactiveBackground from '@/components/ScrollReactiveBackground';
import HoldToConfirmButton from '@/components/HoldToConfirmButton';
import i18nToolsLogo from '@/assets/i18n-tools-logo.png';

// Radial burst particles on completion
const BurstParticles = ({ trigger }: { trigger: boolean }) => {
  const [particles, setParticles] = useState<Array<{ id: number; angle: number; distance: number; size: number; delay: number }>>([]);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    if (trigger && !prefersReducedMotion) {
      // Generate burst particles
      const newParticles = Array.from({ length: 32 }, (_, i) => ({
        id: i,
        angle: (i / 32) * 360 + Math.random() * 20 - 10,
        distance: 80 + Math.random() * 120,
        size: 2 + Math.random() * 4,
        delay: Math.random() * 0.1,
      }));
      setParticles(newParticles);
      
      // Clear after animation
      const timeout = setTimeout(() => setParticles([]), 1000);
      return () => clearTimeout(timeout);
    }
  }, [trigger, prefersReducedMotion]);

  if (particles.length === 0) return null;

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden flex items-center justify-center">
      {particles.map((particle) => {
        const radians = (particle.angle * Math.PI) / 180;
        const endX = Math.cos(radians) * particle.distance;
        const endY = Math.sin(radians) * particle.distance;
        
        return (
          <motion.div
            key={particle.id}
            className="absolute rounded-full bg-primary"
            style={{
              width: particle.size,
              height: particle.size,
            }}
            initial={{ 
              x: 0, 
              y: 0, 
              opacity: 1, 
              scale: 1 
            }}
            animate={{ 
              x: endX, 
              y: endY, 
              opacity: 0, 
              scale: 0.3 
            }}
            transition={{
              duration: 0.6,
              delay: particle.delay,
              ease: [0.25, 0.1, 0.25, 1],
            }}
          />
        );
      })}
    </div>
  );
};

// Floating particles that respond to button hold
const HoldParticles = ({ intensity }: { intensity: number }) => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  if (prefersReducedMotion || intensity === 0) return null;

  const particles = Array.from({ length: 56 }, (_, i) => ({
    id: i,
    x: 5 + Math.random() * 90,
    y: 10 + Math.random() * 80,
    size: 1 + Math.random() * 4,
    delay: Math.random() * 0.003, // Much shorter delay for instant appearance
    duration: 1.2 + Math.random() * 1.0, // Faster cycle
  }));

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-primary/40"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size,
          }}
          initial={{ opacity: intensity * 0.5, scale: 0.8 }} // Start visible immediately
          animate={{
            opacity: [intensity * 0.6, intensity * 0.8, intensity * 0.5, intensity * 0.7, 0],
            scale: [0.8, 1.2, 0.9, 1.1, 0.5],
            y: [0, -25, -15, -40, -60],
          }}
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: "easeOut", // Faster start
          }}
        />
      ))}
    </div>
  );
};

// Closing CTA with parallax and hold-to-confirm button
const ProjectsClosingCTA = ({ t }: { t: (key: string, options?: Record<string, string>) => string }) => {
  const sectionRef = useRef<HTMLElement>(null);
  const [particleIntensity, setParticleIntensity] = useState(0);
  const [burstTrigger, setBurstTrigger] = useState(false);
  
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  });
  
  const backgroundY = useTransform(scrollYProgress, [0, 1], ["0%", "30%"]);
  const glowScale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 1.1]);
  const glowOpacity = useTransform(scrollYProgress, [0, 0.5, 1], [0.2, 0.35, 0.2]);

  return (
    <section ref={sectionRef} className="relative py-32 md:py-40 overflow-hidden">
      {/* Soft top fade transition */}
      <div 
        className="absolute inset-x-0 top-0 h-32 pointer-events-none"
        style={{
          background: 'linear-gradient(to bottom, hsl(var(--background)) 0%, transparent 100%)'
        }}
      />
      
      {/* Subtle ambient background with parallax */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {/* Parallax glow layer */}
        <motion.div 
          className="absolute inset-0"
          style={{ y: backgroundY }}
        >
          <motion.div 
            className="absolute inset-0"
            style={{
              opacity: glowOpacity,
              scale: glowScale,
              background: 'radial-gradient(ellipse 80% 60% at 50% 40%, hsl(var(--primary) / 0.06), transparent 70%)'
            }}
          />
        </motion.div>
        
        {/* Secondary slower parallax layer */}
        <motion.div 
          className="absolute inset-0"
          style={{ 
            y: useTransform(scrollYProgress, [0, 1], ["0%", "15%"]) 
          }}
        >
          <div 
            className="absolute inset-0 opacity-20"
            style={{
              background: 'radial-gradient(ellipse 60% 40% at 30% 60%, hsl(var(--primary) / 0.03), transparent 60%)'
            }}
          />
          <div 
            className="absolute inset-0 opacity-15"
            style={{
              background: 'radial-gradient(ellipse 50% 35% at 70% 30%, hsl(var(--primary) / 0.025), transparent 50%)'
            }}
          />
        </motion.div>
        
        {/* Intensifying glow during hold */}
        <motion.div
          className="absolute inset-0"
          animate={{
            opacity: particleIntensity * 0.3,
          }}
          transition={{ duration: 0.5 }}
          style={{
            background: 'radial-gradient(ellipse 50% 40% at 50% 50%, hsl(var(--primary) / 0.08), transparent 60%)'
          }}
        />
        
        {/* Subtle noise texture overlay (static) */}
        <div 
          className="absolute inset-0 opacity-[0.012]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
            backgroundRepeat: 'repeat'
          }}
        />
      </div>
      
      {/* Floating particles during hold */}
      <HoldParticles intensity={particleIntensity} />

      <div className="container-narrow relative">
        <motion.div
          className="flex flex-col items-center text-center max-w-xl mx-auto"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
        >
          {/* Headline */}
          <h3 className="text-2xl md:text-3xl font-medium text-foreground/95 tracking-tight leading-snug">
            {t('projects.cta.title')}
          </h3>
          
          {/* Supporting line */}
          <p className="mt-5 text-base text-muted-foreground/70 max-w-md">
            {t('projects.cta.subtitle', { defaultValue: "You've seen our work. Let's discuss yours." })}
          </p>
          
          {/* Hold-to-confirm button with burst effect */}
          <motion.div
            className="mt-10 relative"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <HoldToConfirmButton
              targetPath="/contact"
              idleLabel={t('projects.cta.button')}
              holdLabel={t('projects.cta.holdLabel', { defaultValue: "Let's build something great..." })}
              confirmLabel={t('projects.cta.confirmLabel', { defaultValue: "Welcome" })}
              holdDuration={1500}
              onParticleIntensityChange={setParticleIntensity}
              onComplete={() => setBurstTrigger(true)}
            />
            
            {/* Radial burst on completion */}
            <BurstParticles trigger={burstTrigger} />
          </motion.div>
          
          {/* Subtle instruction hint - dims during hold */}
          <motion.p
            className="mt-4 text-xs text-muted-foreground/50"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            animate={{ 
              opacity: particleIntensity > 0 ? 0.2 : 1,
              y: particleIntensity > 0 ? 4 : 0 
            }}
          >
            {t('projects.cta.hint', { defaultValue: "Press and hold when you're ready" })}
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
};

const Projects = () => {
  const { t } = useTranslation();
  const { slug } = useParams();

  const projects = [
    {
      id: '01',
      slug: 'autonomous-supply-chain',
      name: t('projects.items.autonomousSupplyChain.name'),
      description: t('projects.items.autonomousSupplyChain.description'),
      category: t('projects.items.autonomousSupplyChain.category'),
      metric: t('projects.items.autonomousSupplyChain.metric'),
      icon: Activity,
      whatItDoes: 'The system watches your entire supply chain in real time. It spots delays, predicts shortages, and finds where money is being wasted.',
      howItWorks: 'Data flows in from your existing systems. The AI analyzes patterns and flags issues before they become problems. Your team reviews and approves.',
      whatChanges: ['Fewer rush orders', 'Lower inventory costs', 'Faster deliveries', 'Better supplier relationships'],
    },
    {
      id: '02',
      slug: 'financial-risk-engine',
      name: t('projects.items.financialRiskEngine.name'),
      description: t('projects.items.financialRiskEngine.description'),
      category: t('projects.items.financialRiskEngine.category'),
      metric: t('projects.items.financialRiskEngine.metric'),
      icon: BarChart3,
      whatItDoes: 'The engine monitors transactions as they happen. It identifies suspicious patterns and flags potential risks before they escalate.',
      howItWorks: 'Transaction data is analyzed in milliseconds. The system learns from historical patterns and adapts to new threats. Your risk team gets actionable alerts.',
      whatChanges: ['Faster fraud detection', 'Reduced false positives', 'Lower compliance costs', 'Better decision-making'],
    },
    {
      id: '03',
      slug: 'smart-manufacturing-hub',
      name: t('projects.items.smartManufacturingHub.name'),
      description: t('projects.items.smartManufacturingHub.description'),
      category: t('projects.items.smartManufacturingHub.category'),
      metric: t('projects.items.smartManufacturingHub.metric'),
      icon: Cpu,
      whatItDoes: 'The hub coordinates all robotic systems on your production floor. It optimizes scheduling, predicts maintenance needs, and balances workloads.',
      howItWorks: 'Sensors feed real-time data into the system. AI models predict bottlenecks and adjust operations automatically. Your operators stay in control.',
      whatChanges: ['Less downtime', 'Higher throughput', 'Predictable maintenance', 'Smoother operations'],
    },
    {
      id: '04',
      slug: 'i18n-tools',
      name: t('projects.items.i18nTools.name'),
      description: t('projects.items.i18nTools.description'),
      category: t('projects.items.i18nTools.category'),
      metric: t('projects.items.i18nTools.metric'),
      icon: Languages,
      whatItDoes: 'I18N-Tools generates the folder structure, configuration files, and language templates needed for internationalization. Point it at your project, select your target languages, and it scaffolds everything—no manual setup required.',
      howItWorks: 'Pick your project folder. Choose the languages you need. The tool creates your i18n config, translation files, and folder structure. Works with React and react-i18next today. More frameworks coming soon.',
      whatChanges: ['Skip the tedious setup', 'Less copy-paste busywork', 'Same structure every time', 'Ready to start translating'],
    },
  ];

  const heroRef = useRef(null);
  const listRef = useRef(null);

  const heroInView = useInView(heroRef, { once: true });
  const listInView = useInView(listRef, { once: true, margin: "-50px" });

  // If slug is provided, show detail view
  if (slug) {
    const project = projects.find(p => p.slug === slug);
    
    if (!project) {
      return (
        <PageLayout title={t("projects.projectNotFound1")} description="The requested project could not be found.">
          <ScrollReactiveBackground />
          <section className="pt-40 pb-28">
            <div className="container-full">
              <h1 className="heading-hero">{t("projects.projectNotFound")}</h1>
              <Link to="/projects" className="text-primary hover:underline mt-8 inline-block">
                ← Back to Projects
              </Link>
            </div>
          </section>
        </PageLayout>
      );
    }

    const Icon = project.icon;

    return (
      <PageLayout 
        title={project.name} 
        description={project.description}
      >
        <ScrollReactiveBackground />
        
        {/* Back Link */}
        <section className="pt-32 pb-8">
          <div className="container-full">
            <Link 
              to="/projects" 
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Projects
            </Link>
          </div>
        </section>

        {/* Header */}
        <section className="pb-16">
          <div className="container-full">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
              <motion.div
                className="flex-1"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <span className="label-caps text-primary/70 block mb-4">{project.category}</span>
                <h1 className="heading-section mb-6">{project.name}</h1>
                <p className="text-lg text-muted-foreground max-w-2xl">{project.description}</p>
                {project.slug === 'i18n-tools' && (
                  <div className="mt-8">
                    <img 
                      src={i18nToolsLogo} 
                      alt="I18N-Tools" 
                      className="w-16 h-16 md:w-20 md:h-20 object-contain"
                    />
                  </div>
                )}
              </motion.div>

              <motion.div
                className="flex flex-col items-start md:items-end shrink-0"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <span className="text-xs text-muted-foreground mb-2 tracking-wide uppercase">{t("common.real")}</span>
                <div className="inline-flex items-center gap-3 px-5 py-3 bg-primary/10 border border-primary/20 rounded-lg">
                  <Icon className="w-5 h-5 text-primary" />
                  <span className="font-mono text-lg text-primary">{project.metric}</span>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Separator */}
        <div className="container-full">
          <div className="h-px bg-border" />
        </div>

        {/* What It Does */}
        <section className="section-padding">
          <div className="container-full">
            <div className="grid lg:grid-cols-12 gap-12 lg:gap-20">
              <motion.div
                className="lg:col-span-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="heading-section">{t("projects.whatItDoes")}</h2>
                <p className="text-sm text-muted-foreground mt-2">{t("projects.theCoreFunctionSimplyPut")}</p>
              </motion.div>
              <motion.div
                className="lg:col-span-8"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <p className="text-large leading-relaxed">{project.whatItDoes}</p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Separator */}
        <div className="container-full">
          <div className="h-px bg-border" />
        </div>

        {/* How It Works */}
        <section className="section-padding">
          <div className="container-full">
            <div className="grid lg:grid-cols-12 gap-12 lg:gap-20">
              <motion.div
                className="lg:col-span-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="heading-section">{t("projects.howItWorks")}</h2>
                <p className="text-sm text-muted-foreground mt-2">{t("projects.threeStepsYourTeamInControl")}</p>
              </motion.div>
              <motion.div
                className="lg:col-span-8"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                {/* Flow steps */}
                <div className="flex items-center gap-4 mb-8 flex-wrap">
                  {(project.slug === 'i18n-tools' 
                    ? ['Select Project', 'Choose Languages', 'Generate Setup']
                    : ['Observe', 'Predict', 'Suggest']
                  ).map((step, index, arr) => (
                    <div key={step} className="flex items-center gap-4">
                      <span className="text-sm font-mono text-primary/80">{step}</span>
                      {index < arr.length - 1 && <span className="text-muted-foreground/40">→</span>}
                    </div>
                  ))}
                </div>
                <p className="text-large leading-relaxed">{project.howItWorks}</p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Separator */}
        <div className="container-full">
          <div className="h-px bg-border" />
        </div>

        {/* What Changes */}
        <section className="section-padding">
          <div className="container-full">
            <div className="grid lg:grid-cols-12 gap-12 lg:gap-20">
              <motion.div
                className="lg:col-span-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="heading-section">{t("projects.whatChanges")}</h2>
                <p className="text-sm text-muted-foreground mt-2">{t("projects.concreteOutcomesNotPromises")}</p>
              </motion.div>
              <motion.div
                className="lg:col-span-8"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <ul className="space-y-4">
                  {project.whatChanges.map((change, index) => (
                    <li key={index} className="flex items-center gap-4">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary/60" />
                      <span className="text-large">{change}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <ProjectsClosingCTA t={t} />
      </PageLayout>
    );
  }

  // List view
  return (
    <PageLayout 
      title="Projects" 
      description="Explore United Dutch Company's portfolio of AI-driven solutions transforming enterprise operations."
    >
      <ScrollReactiveBackground />
      
      {/* Hero */}
      <section ref={heroRef} className="pt-40 pb-28 relative">
        <div className="container-full">
          <motion.span
            className="label-caps block mb-8"
            initial={{ opacity: 0, y: -40 }}
            animate={heroInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
            {t('projects.hero.label')}
          </motion.span>
          <div className="overflow-hidden pb-4">
            <motion.h1
              className="heading-hero max-w-5xl"
              initial={{ y: 100 }}
              animate={heroInView ? { y: 0 } : {}}
              transition={{ duration: 1, delay: 0.1, ease: [0.25, 0.1, 0.25, 1] }}
            >
              {t('projects.hero.title')}{' '}
              <span className="font-editorial text-primary">{t('projects.hero.titleHighlight')}</span>
            </motion.h1>
          </div>
          <motion.p
            className="text-body max-w-2xl mt-12"
            initial={{ opacity: 0, x: 50 }}
            animate={heroInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            {t('projects.hero.description')}
          </motion.p>
        </div>
      </section>

      {/* Projects List */}
      <section ref={listRef} className="section-padding relative overflow-hidden">
        {/* Subtle tech-inspired background element */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute right-0 top-0 w-1/2 h-full opacity-[0.015]">
            <svg viewBox="0 0 400 800" fill="none" className="w-full h-full">
              <defs>
                <linearGradient id="gridGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.5" />
                  <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
                </linearGradient>
              </defs>
              {/* Abstract grid pattern */}
              {[...Array(12)].map((_, i) => (
                <line key={`h-${i}`} x1="0" y1={i * 70} x2="400" y2={i * 70} stroke="url(#gridGradient)" strokeWidth="0.5" />
              ))}
              {[...Array(8)].map((_, i) => (
                <line key={`v-${i}`} x1={i * 55} y1="0" x2={i * 55} y2="800" stroke="url(#gridGradient)" strokeWidth="0.5" />
              ))}
              {/* Abstract nodes */}
              <circle cx="165" cy="140" r="3" fill="hsl(var(--primary))" opacity="0.3" />
              <circle cx="275" cy="280" r="2" fill="hsl(var(--primary))" opacity="0.2" />
              <circle cx="110" cy="420" r="4" fill="hsl(var(--primary))" opacity="0.25" />
              <circle cx="330" cy="560" r="2.5" fill="hsl(var(--primary))" opacity="0.2" />
            </svg>
          </div>
        </div>

        <div className="container-full relative">
          <div className="max-w-4xl space-y-24 md:space-y-32">
            {projects.map((project, index) => (
              <motion.article
                key={project.id}
                className="group"
                initial={{ opacity: 0, y: 24 }}
                animate={listInView ? { opacity: 1, y: 0 } : {}}
                transition={{ 
                  duration: 0.7, 
                  delay: 0.15 + index * 0.1,
                  ease: [0.25, 0.1, 0.25, 1]
                }}
              >
                <Link to={`/projects/${project.slug}`} className="block">
                  <div className="flex flex-col gap-5">
                    {/* Category & Number */}
                    <div className="flex items-center gap-5">
                      <span className="font-mono text-sm text-primary/60">{project.id}</span>
                      <span className="label-caps text-foreground/35 text-xs tracking-[0.2em]">{project.category}</span>
                    </div>
                    
                    {/* Title - Primary */}
                    <h2 className="heading-medium text-foreground/95 group-hover:text-primary transition-colors duration-300">
                      {project.name}
                    </h2>
                    
                    {/* Description & Metric - Connected */}
                    <div className="flex flex-col md:flex-row md:items-baseline gap-3 md:gap-10 pt-1">
                      <p className="text-foreground/55 text-lg leading-relaxed flex-1">
                        {project.description}
                      </p>
                      <span className="font-mono text-primary/90 text-base font-medium whitespace-nowrap">
                        {project.metric}
                      </span>
                    </div>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* Projects Page Closing CTA */}
      <ProjectsClosingCTA t={t} />
    </PageLayout>
  );
};

export default Projects;