import { motion, useScroll, useTransform, useMotionValue, useSpring } from "framer-motion";
import { useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useIsMobile } from "@/hooks/use-mobile";
import TypewriterWord from "../TypewriterWord";

const HeroSection = () => {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const isMobile = useIsMobile();

  // Mouse tracking - only on desktop
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Smooth spring physics for cursor following
  const smoothMouseX = useSpring(mouseX, {
    stiffness: 50,
    damping: 20,
  });
  const smoothMouseY = useSpring(mouseY, {
    stiffness: 50,
    damping: 20,
  });
  
  useEffect(() => {
    if (isMobile) return; // Skip mouse tracking on mobile
    
    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;
      mouseX.set((clientX / innerWidth - 0.5) * 40);
      mouseY.set((clientY / innerHeight - 0.5) * 30);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY, isMobile]);
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  // Scroll-driven transforms - simplified on mobile
  const contentOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const contentY = isMobile ? 0 : useTransform(scrollYProgress, [0, 0.5], [0, -60]);
  const contentScale = isMobile ? 1 : useTransform(scrollYProgress, [0, 0.5], [1, 0.92]);

  // Ambient lights - only render on desktop
  if (isMobile) {
    return (
      <section ref={containerRef} className="relative min-h-screen flex items-center overflow-hidden">
        <div className="container-full relative z-10 pt-20 flex justify-center">
          <motion.div
            className="max-w-xl md:max-w-3xl lg:max-w-5xl xl:max-w-6xl 2xl:max-w-7xl text-center px-4"
            style={{ opacity: contentOpacity }}
          >
            {/* Label */}
            <motion.span
              className="label-caps block mb-10"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              AI-Powered Efficiency
            </motion.span>

            {/* Main Headline */}
            <motion.h1
              className="heading-hero mb-10 overflow-visible pb-4"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <span className="block">{t("home.we")}</span>
              <span className="block text-foreground/50">systems for the</span>
              <span className="block font-code text-[#ffed85] tracking-tight font-medium text-[1.02em]">
                <TypewriterWord words={["future", "world"]} />
              </span>
            </motion.h1>

            {/* Supporting text */}
            <motion.p
              className="text-body max-w-2xl mx-auto mb-14"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              Intelligent automation that eliminates repetitive work, so you can focus on what truly matters.
            </motion.p>

            {/* CTAs */}
            <motion.div
              className="flex flex-wrap justify-center gap-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              <Link
                to="/projects"
                className="inline-flex items-center px-10 py-5 text-base font-medium bg-primary text-primary-foreground"
              >
                {t("home.exploreProjects")}
              </Link>
              <Link
                to="/contact"
                className="inline-flex items-center px-10 py-5 text-base font-medium border-2 border-border text-foreground"
              >
                Contact
              </Link>
            </motion.div>
          </motion.div>
        </div>

        {/* Mobile scroll hint */}
        <motion.div
          className="absolute bottom-1 left-0 right-0 flex justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.6 }}
          style={{ opacity: contentOpacity }}
        >
          <div className="text-foreground/30">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 9l6 6 6-6" />
            </svg>
          </div>
        </motion.div>
      </section>
    );
  }

  // Desktop: full version with ambient lights
  const light1X = useTransform(scrollYProgress, [0, 0.5], [0, -100]);
  const light1Opacity = useTransform(scrollYProgress, [0, 0.3, 0.5], [0.15, 0.25, 0]);
  const light2X = useTransform(scrollYProgress, [0, 0.5], [0, 80]);
  const light2Opacity = useTransform(scrollYProgress, [0, 0.3, 0.5], [0.12, 0.2, 0]);
  const light3Y = useTransform(scrollYProgress, [0, 0.5], [0, -60]);
  const light3Opacity = useTransform(scrollYProgress, [0, 0.35, 0.5], [0.1, 0.18, 0]);

  return (
    <section ref={containerRef} className="relative min-h-screen flex items-center overflow-hidden">
      {/* Ambient colored lights with pulse and cursor follow */}
      <motion.div
        className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full blur-[120px] pointer-events-none"
        style={{
          background: "radial-gradient(circle, hsl(38 70% 50% / 0.4) 0%, transparent 70%)",
          x: smoothMouseX,
          y: smoothMouseY,
          translateX: light1X,
          opacity: light1Opacity,
        }}
        animate={{
          scale: [1, 1.15, 1],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute top-1/3 right-1/4 w-[400px] h-[400px] rounded-full blur-[100px] pointer-events-none"
        style={{
          background: "radial-gradient(circle, hsl(25 60% 45% / 0.35) 0%, transparent 70%)",
          x: useTransform(smoothMouseX, (v) => v * -0.7),
          y: useTransform(smoothMouseY, (v) => v * -0.5),
          translateX: light2X,
          opacity: light2Opacity,
        }}
        animate={{
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1.5,
        }}
      />
      <motion.div
        className="absolute bottom-1/4 left-1/3 w-[350px] h-[350px] rounded-full blur-[90px] pointer-events-none"
        style={{
          background: "radial-gradient(circle, hsl(45 65% 55% / 0.3) 0%, transparent 70%)",
          x: useTransform(smoothMouseX, (v) => v * 0.5),
          y: smoothMouseY,
          translateY: light3Y,
          opacity: light3Opacity,
        }}
        animate={{
          scale: [1, 1.18, 1],
        }}
        transition={{
          duration: 4.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.8,
        }}
      />
      <div className="container-full relative z-10 pt-20 flex justify-center">
        <motion.div
          className="max-w-xl md:max-w-3xl lg:max-w-5xl xl:max-w-6xl 2xl:max-w-7xl text-center px-4"
          style={{
            opacity: contentOpacity,
            y: contentY,
            scale: contentScale,
          }}
        >
          {/* Label - fade up with blur */}
          <motion.span
            className="label-caps block mb-10"
            initial={{
              opacity: 0,
              y: 30,
              filter: "blur(10px)",
            }}
            animate={{
              opacity: 1,
              y: 0,
              filter: "blur(0px)",
            }}
            transition={{
              duration: 1,
              delay: 0.2,
              ease: [0.22, 1, 0.36, 1],
            }}
          >
            AI-Powered Efficiency
          </motion.span>

          {/* Main Headline - split line animation */}
          <motion.h1
            className="heading-hero mb-10 overflow-visible pb-4"
            initial={{
              opacity: 0,
            }}
            animate={{
              opacity: 1,
            }}
            transition={{
              duration: 0.3,
              delay: 0.3,
            }}
          >
            <motion.span
              className="block"
              initial={{
                opacity: 0,
                y: 80,
                rotateX: 40,
              }}
              animate={{
                opacity: 1,
                y: 0,
                rotateX: 0,
              }}
              transition={{
                duration: 1,
                delay: 0.4,
                ease: [0.22, 1, 0.36, 1],
              }}
            >
              We build intelligent
            </motion.span>
            <motion.span
              className="block"
              initial={{
                opacity: 0,
                y: 80,
                rotateX: 40,
              }}
              animate={{
                opacity: 1,
                y: 0,
                rotateX: 0,
              }}
              transition={{
                duration: 1,
                delay: 0.55,
                ease: [0.22, 1, 0.36, 1],
              }}
            >
              <span className="text-foreground/50">systems for the</span>
            </motion.span>
            <motion.span
              className="block"
              initial={{
                opacity: 0,
                y: 80,
                rotateX: 40,
              }}
              animate={{
                opacity: 1,
                y: 0,
                rotateX: 0,
              }}
              transition={{
                duration: 1,
                delay: 0.7,
                ease: [0.22, 1, 0.36, 1],
              }}
            >
              <span className="font-code text-[#ffed85] inline-flex justify-center tracking-tight font-medium text-[1.02em]">
                <TypewriterWord words={["future", "world"]} />
              </span>
            </motion.span>
          </motion.h1>

          {/* Supporting text - fade up with blur */}
          <motion.p
            className="text-body max-w-2xl mx-auto mb-14"
            initial={{
              opacity: 0,
              y: 30,
              filter: "blur(8px)",
            }}
            animate={{
              opacity: 1,
              y: 0,
              filter: "blur(0px)",
            }}
            transition={{
              duration: 1,
              delay: 0.8,
              ease: [0.22, 1, 0.36, 1],
            }}
          >
            Intelligent automation that eliminates repetitive work, so you can focus on what truly matters.
          </motion.p>

          {/* CTAs - staggered scale up */}
          <motion.div
            className="flex flex-wrap justify-center gap-6"
            initial={{
              opacity: 0,
            }}
            animate={{
              opacity: 1,
            }}
            transition={{
              duration: 0.3,
              delay: 1,
            }}
          >
            <motion.div
              initial={{
                opacity: 0,
                y: 30,
                scale: 0.9,
              }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1,
              }}
              transition={{
                duration: 0.8,
                delay: 1.1,
                ease: [0.22, 1, 0.36, 1],
              }}
              whileTap={{
                scale: 0.98,
              }}
              className="relative"
            >
              {/* Glowing pulse effect */}
              <motion.div
                className="absolute inset-0 bg-primary rounded-sm"
                animate={{
                  boxShadow: [
                    "0 0 20px hsl(var(--primary) / 0.4), 0 0 40px hsl(var(--primary) / 0.2)",
                    "0 0 30px hsl(var(--primary) / 0.6), 0 0 60px hsl(var(--primary) / 0.3)",
                    "0 0 20px hsl(var(--primary) / 0.4), 0 0 40px hsl(var(--primary) / 0.2)",
                  ],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
              <Link
                to="/projects"
                className="group relative inline-flex items-center px-10 py-5 text-base font-medium bg-primary text-primary-foreground overflow-hidden"
              >
                {/* Shine sweep effect */}
                <span className="absolute inset-0 translate-x-[-100%] bg-gradient-to-r from-transparent via-primary-foreground/30 to-transparent group-hover:translate-x-[100%] transition-transform duration-700 ease-out" />
                <span className="relative z-10">{t("home.exploreProjects")}</span>
              </Link>
            </motion.div>
            <motion.div
              initial={{
                opacity: 0,
                y: 30,
                scale: 0.9,
              }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1,
              }}
              transition={{
                duration: 0.8,
                delay: 1.25,
                ease: [0.22, 1, 0.36, 1],
              }}
              whileTap={{
                scale: 0.98,
              }}
            >
              <Link
                to="/contact"
                className="group relative inline-flex items-center px-10 py-5 text-base font-medium border-2 border-border text-foreground overflow-hidden transition-colors duration-300 hover:border-primary hover:text-primary-foreground"
              >
                {/* Swipe background */}
                <span className="absolute inset-0 bg-primary translate-x-[-101%] group-hover:translate-x-0 transition-transform duration-300 ease-out" />
                <span className="relative z-10">Contact</span>
              </Link>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      {/* Mobile scroll hint - subtle bouncing chevron */}
      <motion.div
        className="absolute bottom-1 left-0 right-0 flex md:hidden justify-center"
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: 1,
        }}
        transition={{
          delay: 1.5,
          duration: 0.6,
        }}
        style={{
          opacity: contentOpacity,
        }}
      >
        <motion.div
          animate={{
            y: [0, 6, 0],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="text-foreground/30"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </motion.div>
      </motion.div>

      {/* Desktop scroll indicator */}
      <motion.div
        className="absolute bottom-1 left-0 right-0 hidden md:flex justify-center"
        initial={{
          opacity: 0,
          y: 30,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          delay: 1.1,
          duration: 0.6,
        }}
        style={{
          opacity: contentOpacity,
        }}
      >
        <div className="flex flex-col items-center gap-4 mt-[20px]">
          <span className="label-caps text-foreground/40">Scroll</span>
          <div className="w-px h-12 bg-gradient-to-b from-primary/60 to-transparent" />
        </div>
      </motion.div>
    </section>
  );
};
export default HeroSection;
