import { Canvas, useFrame } from '@react-three/fiber';
import { useRef, useMemo, useState, useEffect } from 'react';
import * as THREE from 'three';
import { Line } from '@react-three/drei';
import { motion } from 'framer-motion';

const PulsingNode = ({ position, color, baseSize = 0.035 }: { position: THREE.Vector3, color: string, baseSize?: number }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshBasicMaterial>(null);
  const phaseOffset = useMemo(() => Math.random() * Math.PI * 2, []);
  
  useFrame((state) => {
    const time = state.clock.elapsedTime;
    const pulse = Math.sin(time * 1.5 + phaseOffset) * 0.5 + 0.5;
    
    if (meshRef.current) {
      const scale = 1 + pulse * 0.3;
      meshRef.current.scale.setScalar(scale);
    }
    if (materialRef.current) {
      materialRef.current.opacity = 0.5 + pulse * 0.4;
    }
  });
  
  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[baseSize, 8, 8]} />
      <meshBasicMaterial 
        ref={materialRef}
        color={color} 
        transparent 
        opacity={0.7}
      />
    </mesh>
  );
};

const TravelingLight = ({ path, speed = 0.3, color, size = 0.05 }: { path: THREE.Vector3[], speed?: number, color: string, size?: number }) => {
  const mainLightRef = useRef<THREE.Mesh>(null);
  const mainMaterialRef = useRef<THREE.MeshBasicMaterial>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const glowMaterialRef = useRef<THREE.MeshBasicMaterial>(null);
  const trailSegmentsRef = useRef<THREE.Mesh[]>([]);
  const phaseOffset = useMemo(() => Math.random() * Math.PI * 2, []);
  const trailLength = 20; // More points for smoother trail
  
  const getPositionAtT = (t: number) => {
    const normalizedT = ((t % 1) + 1) % 1;
    const totalSegments = path.length - 1;
    const segmentIndex = Math.floor(normalizedT * totalSegments);
    const segmentT = (normalizedT * totalSegments) % 1;
    
    const startPoint = path[Math.min(segmentIndex, path.length - 1)];
    const endPoint = path[Math.min(segmentIndex + 1, path.length - 1)];
    
    if (startPoint && endPoint) {
      return new THREE.Vector3().lerpVectors(startPoint, endPoint, segmentT);
    }
    return startPoint?.clone() || new THREE.Vector3();
  };
  
  useFrame((state) => {
    if (path.length < 2) return;
    
    const time = state.clock.elapsedTime * speed + phaseOffset;
    
    // Update main light position
    const mainPos = getPositionAtT(time);
    if (mainLightRef.current) {
      mainLightRef.current.position.copy(mainPos);
    }
    
    // Update outer glow position
    if (glowRef.current) {
      glowRef.current.position.copy(mainPos);
    }
    
    // Pulsing glow effect on main light - more subtle and realistic
    const pulse = Math.sin(state.clock.elapsedTime * 4 + phaseOffset) * 0.15 + 0.85;
    if (mainMaterialRef.current) {
      mainMaterialRef.current.opacity = pulse;
    }
    if (glowMaterialRef.current) {
      glowMaterialRef.current.opacity = pulse * 0.35;
    }
    
    // Update trail segments with gradient opacity and size
    trailSegmentsRef.current.forEach((mesh, i) => {
      if (mesh) {
        const trailOffset = (i + 1) * 0.006; // Tighter spacing for smoother trail
        const pos = getPositionAtT(time - trailOffset);
        mesh.position.copy(pos);
        
        // Exponential falloff for more realistic comet-like trail
        const progress = i / trailLength;
        const falloff = Math.pow(1 - progress, 2.5);
        
        // Scale decreases along trail (tapered effect)
        const scale = falloff * 0.85 + 0.15;
        mesh.scale.setScalar(scale);
        
        // Opacity fades along trail with smooth falloff
        const material = mesh.material as THREE.MeshBasicMaterial;
        if (material) {
          material.opacity = falloff * 0.7;
        }
      }
    });
  });
  
  // Create trail segment refs
  const trailSegments = useMemo(() => {
    return Array.from({ length: trailLength }, (_, i) => i);
  }, []);
  
  return (
    <group>
      {/* Outer glow sphere */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[size * 2.5, 16, 16]} />
        <meshBasicMaterial 
          ref={glowMaterialRef}
          color={color} 
          transparent 
          opacity={0.3}
          depthWrite={false}
        />
      </mesh>
      {/* Main light - brighter core */}
      <mesh ref={mainLightRef}>
        <sphereGeometry args={[size, 12, 12]} />
        <meshBasicMaterial 
          ref={mainMaterialRef}
          color={color} 
          transparent 
          opacity={0.95}
        />
      </mesh>
      {/* Trail segments - individual spheres for gradient effect */}
      {trailSegments.map((_, i) => (
        <mesh
          key={`trail-${i}`}
          ref={(el) => {
            if (el) trailSegmentsRef.current[i] = el;
          }}
        >
          <sphereGeometry args={[size * 0.7, 8, 8]} />
          <meshBasicMaterial 
            color={color} 
            transparent 
            opacity={0.5}
            depthWrite={false}
          />
        </mesh>
      ))}
    </group>
  );
};

const HolographicLock = () => {
  const lockRef = useRef<THREE.Group>(null);
  const shackleRef = useRef<THREE.Group>(null);
  const unlockPhaseRef = useRef(0);
  
  // Gold system colors matching globe
  const hologramColor = '#D4AF37';
  const glowColor = '#FFD700';

  useFrame((state) => {
    if (lockRef.current) {
      // Slow floating rotation in all directions
      const time = state.clock.elapsedTime;
      lockRef.current.rotation.y = time * 0.15; // Slow continuous Y rotation
      lockRef.current.rotation.x = Math.sin(time * 0.1) * 0.15 + 0.2; // Gentle X oscillation
      lockRef.current.rotation.z = Math.sin(time * 0.08) * 0.1; // Subtle Z wobble
    }
    
    // Lock/unlock cycle - every 10 seconds for calm pacing
    const cycleTime = state.clock.elapsedTime % 10;
    
    // Unlock from 4-5s, stay unlocked 5-6s, lock from 6-7s
    let targetUnlock = 0;
    if (cycleTime >= 4 && cycleTime < 5) {
      targetUnlock = (cycleTime - 4); // 0 to 1
    } else if (cycleTime >= 5 && cycleTime < 6) {
      targetUnlock = 1; // Stay unlocked
    } else if (cycleTime >= 6 && cycleTime < 7) {
      targetUnlock = 1 - (cycleTime - 6); // 1 to 0
    }
    
    // Smooth interpolation
    unlockPhaseRef.current += (targetUnlock - unlockPhaseRef.current) * 0.08;
    const unlockPhase = unlockPhaseRef.current;
    
    // Animate shackle
    if (shackleRef.current) {
      shackleRef.current.position.y = unlockPhase * 0.35;
      shackleRef.current.rotation.z = unlockPhase * 0.2;
    }
  });

  // Lock body - square shape like a classic padlock
  const bodyLines = useMemo(() => {
    const lines: THREE.Vector3[][] = [];
    const width = 0.9;
    const height = 0.9; // Square proportions
    const depth = 0.35;
    const cornerRadius = 0.1;
    const segments = 8;
    
    // Create horizontal slices at different depths
    for (let d = 0; d <= 4; d++) {
      const z = -depth/2 + (d / 4) * depth;
      const points: THREE.Vector3[] = [];
      
      // Rounded rectangle
      const steps = 48;
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        let x, y;
        
        if (t < 0.25) {
          // Top edge
          const tt = t / 0.25;
          x = -width/2 + cornerRadius + tt * (width - 2 * cornerRadius);
          y = height/2;
        } else if (t < 0.5) {
          // Right edge
          const tt = (t - 0.25) / 0.25;
          x = width/2;
          y = height/2 - cornerRadius - tt * (height - 2 * cornerRadius);
        } else if (t < 0.75) {
          // Bottom edge
          const tt = (t - 0.5) / 0.25;
          x = width/2 - cornerRadius - tt * (width - 2 * cornerRadius);
          y = -height/2;
        } else {
          // Left edge
          const tt = (t - 0.75) / 0.25;
          x = -width/2;
          y = -height/2 + cornerRadius + tt * (height - 2 * cornerRadius);
        }
        
        points.push(new THREE.Vector3(x, y, z));
      }
      lines.push(points);
    }
    
    // Vertical connecting lines
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const x = Math.cos(angle) * width * 0.45;
      const y = Math.sin(angle) * height * 0.45;
      
      lines.push([
        new THREE.Vector3(x, y, -depth/2),
        new THREE.Vector3(x, y, depth/2),
      ]);
    }
    
    return lines;
  }, []);

  // Shackle - proper upside-down U shape like a real padlock
  const shacklePath = useMemo(() => {
    const points: THREE.Vector3[] = [];
    const width = 0.45;
    const legHeight = 0.75; // Taller legs for classic padlock proportions
    const arcRadius = width / 2;
    
    // Left leg going up (straight vertical)
    for (let i = 0; i <= 12; i++) {
      const t = i / 12;
      points.push(new THREE.Vector3(-width/2, t * legHeight, 0));
    }
    
    // Semicircular arc over top (from left to right, curving upward)
    for (let i = 0; i <= 24; i++) {
      const angle = Math.PI - (i / 24) * Math.PI; // from π to 0
      const x = Math.cos(angle) * arcRadius;
      const y = legHeight + Math.sin(angle) * arcRadius;
      points.push(new THREE.Vector3(x, y, 0));
    }
    
    // Right leg going down (straight vertical)
    for (let i = 0; i <= 12; i++) {
      const t = i / 12;
      points.push(new THREE.Vector3(width/2, legHeight * (1 - t), 0));
    }
    
    return points;
  }, []);

  // Orbital rings (like globe meridians) with point positions
  const orbitalData = useMemo(() => {
    const rings: { points: THREE.Vector3[], nodePositions: THREE.Vector3[] }[] = [];
    
    // Horizontal rings at different heights
    for (let h = 0; h < 3; h++) {
      const y = -0.3 + h * 0.3;
      const radius = 1.5 - Math.abs(h - 1) * 0.2;
      const points: THREE.Vector3[] = [];
      const nodePositions: THREE.Vector3[] = [];
      
      for (let i = 0; i <= 64; i++) {
        const angle = (i / 64) * Math.PI * 2;
        const point = new THREE.Vector3(
          Math.cos(angle) * radius,
          y,
          Math.sin(angle) * radius * 0.6
        );
        points.push(point);
        
        // Add node positions at regular intervals (fewer points)
        if (i % 16 === 0 && i < 64) {
          nodePositions.push(point.clone());
        }
      }
      rings.push({ points, nodePositions });
    }
    
    // Tilted orbital ring
    const tiltPoints: THREE.Vector3[] = [];
    const tiltNodePositions: THREE.Vector3[] = [];
    const tiltRadius = 1.6;
    for (let i = 0; i <= 64; i++) {
      const angle = (i / 64) * Math.PI * 2;
      const x = Math.cos(angle) * tiltRadius;
      const baseY = Math.sin(angle) * tiltRadius * 0.3;
      const z = Math.sin(angle) * tiltRadius * 0.5;
      const point = new THREE.Vector3(x, baseY, z);
      tiltPoints.push(point);
      
      if (i % 21 === 0 && i < 64) {
        tiltNodePositions.push(point.clone());
      }
    }
    rings.push({ points: tiltPoints, nodePositions: tiltNodePositions });
    
    return rings;
  }, []);

  // Security nodes floating around
  const securityNodes = useMemo(() => {
    return Array.from({ length: 12 }, (_, i) => {
      const angle = (i / 12) * Math.PI * 2;
      const radius = 1.3 + (i % 3) * 0.2;
      const heightOffset = Math.sin(angle * 2) * 0.3;
      return {
        position: new THREE.Vector3(
          Math.cos(angle) * radius,
          heightOffset,
          Math.sin(angle) * radius * 0.5
        ),
        size: 0.025 + (i % 4) * 0.01,
      };
    });
  }, []);

  // Connection arcs between nodes
  const connectionArcs = useMemo(() => {
    const arcs: THREE.Vector3[][] = [];
    for (let i = 0; i < 6; i++) {
      const start = securityNodes[i].position;
      const end = securityNodes[(i + 2) % 12].position;
      const mid = new THREE.Vector3(
        (start.x + end.x) / 2,
        (start.y + end.y) / 2 + 0.15,
        (start.z + end.z) / 2
      );
      
      const points: THREE.Vector3[] = [];
      for (let t = 0; t <= 10; t++) {
        const tt = t / 10;
        const p = new THREE.Vector3();
        p.x = (1 - tt) * (1 - tt) * start.x + 2 * (1 - tt) * tt * mid.x + tt * tt * end.x;
        p.y = (1 - tt) * (1 - tt) * start.y + 2 * (1 - tt) * tt * mid.y + tt * tt * end.y;
        p.z = (1 - tt) * (1 - tt) * start.z + 2 * (1 - tt) * tt * mid.z + tt * tt * end.z;
        points.push(p);
      }
      arcs.push(points);
    }
    return arcs;
  }, [securityNodes]);

  return (
    <group ref={lockRef} rotation={[0.2, 0, 0]}>
      {/* Lock body wireframe */}
      {bodyLines.map((points, i) => (
        <Line
          key={`body-${i}`}
          points={points}
          color={hologramColor}
          lineWidth={i < 5 ? 1.5 : 1}
          transparent
          opacity={i < 5 ? 0.7 : 0.4}
          depthWrite={false}
          renderOrder={2}
        />
      ))}

      {/* Shackle - animated */}
      <group ref={shackleRef} position={[0, 0.425, 0]}>
        <Line
          points={shacklePath}
          color={glowColor}
          lineWidth={4}
          transparent
          opacity={0.9}
          depthWrite={false}
          renderOrder={3}
        />
        {/* Depth lines for shackle */}
        {[-0.1, 0.1].map((z, i) => (
          <Line
            key={`shackle-d-${i}`}
            points={shacklePath.map(p => new THREE.Vector3(p.x, p.y, z))}
            color={hologramColor}
            lineWidth={2}
            transparent
            opacity={0.4}
            depthWrite={false}
            renderOrder={2}
          />
        ))}
      </group>

      {/* Keyhole - circle on top, slot below */}
      <group position={[0, 0.05, 0.2]}>
        {/* Keyhole circle (top part) */}
        <mesh>
          <ringGeometry args={[0.06, 0.09, 24]} />
          <meshBasicMaterial 
            color={glowColor} 
            transparent 
            opacity={0.8}
            side={THREE.DoubleSide}
          />
        </mesh>
        {/* Keyhole slot (bottom part) */}
        <mesh position={[0, -0.12, 0]}>
          <planeGeometry args={[0.05, 0.15]} />
          <meshBasicMaterial 
            color={glowColor} 
            transparent 
            opacity={0.6}
            side={THREE.DoubleSide}
          />
        </mesh>
        {/* Keyhole slot outline */}
        <Line
          points={[
            new THREE.Vector3(-0.025, 0, 0.01),
            new THREE.Vector3(-0.025, -0.19, 0.01),
            new THREE.Vector3(0.025, -0.19, 0.01),
            new THREE.Vector3(0.025, 0, 0.01),
          ]}
          color={glowColor}
          lineWidth={1.5}
          transparent
          opacity={0.7}
        />
      </group>

      {/* Orbital rings - thicker with points and traveling lights */}
      {orbitalData.map((ring, i) => (
        <group key={`orbital-group-${i}`}>
          <Line
            points={ring.points}
            color={hologramColor}
            lineWidth={2}
            transparent
            opacity={0.4}
            depthWrite={false}
            renderOrder={1}
          />
          {/* Traveling light along the orbital */}
          <TravelingLight 
            path={ring.points} 
            speed={0.06 + i * 0.02} 
            color={glowColor}
            size={0.045}
          />
          {/* Pulsing points on the orbital rings */}
          {ring.nodePositions.map((pos, j) => (
            <PulsingNode 
              key={`orbital-node-${i}-${j}`} 
              position={pos} 
              color={glowColor}
            />
          ))}
        </group>
      ))}


      {/* Connection arcs */}
      {connectionArcs.map((points, i) => (
        <Line
          key={`arc-${i}`}
          points={points}
          color={hologramColor}
          lineWidth={0.5}
          transparent
          opacity={0.15}
          depthWrite={false}
          renderOrder={1}
        />
      ))}
    </group>
  );
};

const WireframeLock = () => {
  const [shouldAnimate, setShouldAnimate] = useState(true);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setShouldAnimate(!mediaQuery.matches);
    
    const handler = (e: MediaQueryListEvent) => setShouldAnimate(!e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-[5]">
      {/* Ambient glow background with pulsing animation */}
      <motion.div 
        className="absolute left-1/2 top-[40%] -translate-x-1/2 -translate-y-1/2 w-[400px] md:w-[900px] h-[400px] md:h-[900px] lg:w-[1100px] lg:h-[1100px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 40%, transparent 70%)',
        }}
        animate={{
          opacity: [0.2, 0.4, 0.2],
          scale: [0.95, 1.02, 0.95],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Mobile fallback - CSS hidden on desktop */}
      <div className="md:hidden absolute left-1/2 top-[35%] -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
        <div 
          className="w-20 h-24 border-2 border-primary/30 rounded-lg relative"
          style={{ boxShadow: '0 0 30px rgba(212, 175, 55, 0.15)' }}
        >
          <div 
            className="absolute -top-5 left-1/2 -translate-x-1/2 w-10 h-8 border-2 border-primary/40 rounded-t-full"
          />
        </div>
      </div>

      {/* Desktop 3D Canvas - CSS hidden on mobile */}
      <div className="hidden md:block absolute left-1/2 -translate-x-1/2 top-[20%] md:top-[25%] w-[500px] h-[500px] md:w-[700px] md:h-[700px] lg:w-[850px] lg:h-[850px]">
        <div className="w-full h-full opacity-40 md:opacity-50">
          {shouldAnimate ? (
            <Canvas
              camera={{ position: [0, 0.3, 4], fov: 50 }}
              style={{ background: 'transparent' }}
            >
              <ambientLight intensity={0.5} />
              <HolographicLock />
            </Canvas>
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <div 
                className="w-24 h-32 md:w-32 md:h-40 border-2 border-primary/40 rounded-lg relative"
                style={{ boxShadow: '0 0 30px rgba(212, 175, 55, 0.2)' }}
              >
                <div 
                  className="absolute -top-6 left-1/2 -translate-x-1/2 w-12 md:w-16 h-8 md:h-10 border-2 border-primary/60 rounded-t-full"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-[40%] bg-gradient-to-t from-background via-background/80 to-transparent pointer-events-none" />
    </div>
  );
};

export default WireframeLock;
