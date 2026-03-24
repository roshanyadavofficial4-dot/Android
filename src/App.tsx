import React, { useEffect, useState, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Cpu, MemoryStick, Activity, Mic, Volume2, ShieldAlert, CheckCircle2, Maximize2, Move } from 'lucide-react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Sphere, MeshDistortMaterial, Float } from '@react-three/drei';
import * as THREE from 'three';

interface SystemTelemetry {
  cpu: number;
  ram: number;
}

function HolographicSphere({ rotation, scale, position, status }: { 
  rotation: [number, number, number], 
  scale: number, 
  position: [number, number, number],
  status: string 
}) {
  const pointsRef = useRef<THREE.Points>(null);
  const sphereRef = useRef<THREE.Mesh>(null);
  
  // Generate random points for the particle cloud
  const particles = useMemo(() => {
    const count = 2000;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 1.5 + Math.random() * 0.5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    return positions;
  }, []);

  useFrame((state) => {
    if (pointsRef.current) {
      // Vibration effect
      const time = state.clock.getElapsedTime();
      pointsRef.current.rotation.y += 0.002;
      pointsRef.current.rotation.x += 0.001;
      
      // Vibrate particles based on status
      const vibrationIntensity = status === 'processing' ? 0.05 : 0.01;
      const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < positions.length; i++) {
        positions[i] += (Math.random() - 0.5) * vibrationIntensity;
      }
      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
    
    if (sphereRef.current) {
      sphereRef.current.rotation.y += 0.005;
    }
  });

  return (
    <group rotation={rotation} scale={scale} position={position}>
      {/* Core Sphere */}
      <Sphere args={[1, 64, 64]} ref={sphereRef}>
        <MeshDistortMaterial
          color="#00ffff"
          speed={2}
          distort={0.3}
          radius={1}
          opacity={0.2}
          transparent
          wireframe
        />
      </Sphere>

      {/* Particle Cloud */}
      <Points ref={pointsRef} positions={particles} stride={3}>
        <PointMaterial
          transparent
          color="#00ffff"
          size={0.02}
          sizeAttenuation={true}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </Points>

      {/* Outer Glow Rings */}
      <Float speed={2} rotationIntensity={1} floatIntensity={1}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1.8, 0.01, 16, 100]} />
          <meshBasicMaterial color="#00ffff" transparent opacity={0.3} />
        </mesh>
        <mesh rotation={[0, Math.PI / 2, 0]}>
          <torusGeometry args={[2.0, 0.01, 16, 100]} />
          <meshBasicMaterial color="#0088ff" transparent opacity={0.2} />
        </mesh>
      </Float>
    </group>
  );
}

export default function App() {
  const [status, setStatus] = useState<'idle' | 'listening' | 'processing' | 'speaking'>('idle');
  const [subtitle, setSubtitle] = useState<string>('A.R.Y.A. OS Online. Awaiting commands, Sir.');
  const [telemetry, setTelemetry] = useState<SystemTelemetry>({ cpu: 0, ram: 0 });
  const [logs, setLogs] = useState<{ id: number; text: string; type: 'info' | 'success' | 'error' }[]>([]);
  const logIdCounter = useRef(0);

  // 3D Control State
  const [sphereRotation, setSphereRotation] = useState<[number, number, number]>([0, 0, 0]);
  const [sphereScale, setSphereScale] = useState<number>(1);
  const [spherePosition, setSpherePosition] = useState<[number, number, number]>([0, 0, 0]);

  const addLog = (text: string, type: 'info' | 'success' | 'error' = 'info') => {
    setLogs((prev) => {
      const newLogs = [...prev, { id: logIdCounter.current++, text, type }];
      if (newLogs.length > 5) newLogs.shift();
      return newLogs;
    });
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');

    ws.onopen = () => {
      addLog('WebSocket connected to A.R.Y.A. Core', 'success');
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        const { type, data } = message;

        switch (type) {
          case 'speak':
            setStatus('speaking');
            setSubtitle(data.text);
            addLog(`A.R.Y.A.: ${data.text}`, 'info');
            setTimeout(() => setStatus('idle'), Math.max(3000, data.text.length * 50));
            break;
          case 'cpu':
            setTelemetry((prev) => ({ ...prev, cpu: data.percent || 0 }));
            break;
          case 'ram':
            setTelemetry((prev) => ({ ...prev, ram: data.percent || 0 }));
            break;
          case 'listen':
            setStatus('listening');
            setSubtitle('Listening...');
            addLog('Microphone active. Listening for commands...', 'info');
            break;
          case 'processing':
            setStatus('processing');
            setSubtitle('Processing command...');
            addLog('Processing audio input...', 'info');
            break;
          case 'gesture_control':
            // Handle 3D manipulation from backend
            if (data.rotation) setSphereRotation(data.rotation);
            if (data.scale) setSphereScale(data.scale);
            if (data.position) setSpherePosition(data.position);
            addLog(`Gesture Control: ${data.action}`, 'info');
            break;
          case 'action_result':
            if (data.status === 'Success') {
              addLog(`Action successful: ${data.action || 'Unknown'}`, 'success');
            } else {
              addLog(`Action failed: ${data.reason || 'Unknown error'}`, 'error');
            }
            break;
          default:
            break;
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };

    ws.onerror = () => {
      addLog('WebSocket connection error', 'error');
    };

    ws.onclose = () => {
      addLog('WebSocket disconnected', 'error');
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#050B14] text-cyan-400 font-mono overflow-hidden relative flex flex-col items-center justify-center">
      {/* Background Grid & Vignette */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#050B14_100%)] pointer-events-none" />

      {/* Top Header */}
      <header className="absolute top-6 left-0 right-0 flex justify-between px-10 items-start z-10">
        <div className="flex flex-col">
          <h1 className="text-3xl font-bold tracking-[0.3em] text-cyan-300 drop-shadow-[0_0_10px_rgba(0,255,255,0.8)]">A.R.Y.A. OS</h1>
          <span className="text-xs tracking-widest text-cyan-600 mt-1 uppercase">Advanced Responsive Yield Automaton</span>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 text-cyan-500">
            <Activity className="w-5 h-5 animate-pulse" />
            <span className="text-sm uppercase tracking-widest">System Online</span>
          </div>
          <div className="flex items-center space-x-2 text-cyan-500 border-l border-cyan-500/30 pl-6">
            <Maximize2 className="w-4 h-4" />
            <span className="text-xs uppercase tracking-widest">Gesture Link Active</span>
          </div>
        </div>
      </header>

      {/* Left Panel: Telemetry */}
      <aside className="absolute left-10 top-1/2 -translate-y-1/2 flex flex-col space-y-8 w-64 z-10">
        <div className="border border-cyan-500/30 bg-cyan-950/20 p-4 rounded-lg backdrop-blur-sm shadow-[0_0_15px_rgba(0,255,255,0.1)]">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2 text-cyan-300">
              <Cpu className="w-4 h-4" />
              <span className="text-sm tracking-widest uppercase">CPU Core</span>
            </div>
            <span className="text-xs">{telemetry.cpu.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-cyan-950 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(0,255,255,0.8)]"
              initial={{ width: 0 }}
              animate={{ width: `${telemetry.cpu}%` }}
              transition={{ type: 'spring', bounce: 0, duration: 0.5 }}
            />
          </div>
        </div>

        <div className="border border-cyan-500/30 bg-cyan-950/20 p-4 rounded-lg backdrop-blur-sm shadow-[0_0_15px_rgba(0,255,255,0.1)]">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2 text-cyan-300">
              <MemoryStick className="w-4 h-4" />
              <span className="text-sm tracking-widest uppercase">Memory</span>
            </div>
            <span className="text-xs">{telemetry.ram.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-cyan-950 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(0,255,255,0.8)]"
              initial={{ width: 0 }}
              animate={{ width: `${telemetry.ram}%` }}
              transition={{ type: 'spring', bounce: 0, duration: 0.5 }}
            />
          </div>
        </div>

        {/* 3D Status */}
        <div className="border border-cyan-500/30 bg-cyan-950/20 p-4 rounded-lg backdrop-blur-sm">
          <h4 className="text-[10px] uppercase tracking-widest text-cyan-600 mb-2">Spatial Data</h4>
          <div className="grid grid-cols-2 gap-2 text-[10px]">
            <div className="flex justify-between"><span>ROT X:</span> <span>{sphereRotation[0].toFixed(2)}</span></div>
            <div className="flex justify-between"><span>ROT Y:</span> <span>{sphereRotation[1].toFixed(2)}</span></div>
            <div className="flex justify-between"><span>SCALE:</span> <span>{sphereScale.toFixed(2)}</span></div>
            <div className="flex justify-between"><span>POS Z:</span> <span>{spherePosition[2].toFixed(2)}</span></div>
          </div>
        </div>
      </aside>

      {/* Right Panel: Event Logs */}
      <aside className="absolute right-10 top-1/2 -translate-y-1/2 flex flex-col w-72 z-10 border border-cyan-500/20 bg-cyan-950/10 p-4 rounded-lg backdrop-blur-sm h-80 overflow-hidden">
        <h3 className="text-xs tracking-widest uppercase text-cyan-600 mb-4 border-b border-cyan-500/20 pb-2">System Logs</h3>
        <div className="flex flex-col space-y-3 justify-end h-full">
          <AnimatePresence initial={false}>
            {logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-start space-x-2 text-xs"
              >
                {log.type === 'info' && <Activity className="w-3 h-3 text-cyan-500 mt-0.5 shrink-0" />}
                {log.type === 'success' && <CheckCircle2 className="w-3 h-3 text-emerald-400 mt-0.5 shrink-0" />}
                {log.type === 'error' && <ShieldAlert className="w-3 h-3 text-red-400 mt-0.5 shrink-0" />}
                <span className={`${log.type === 'error' ? 'text-red-300' : log.type === 'success' ? 'text-emerald-300' : 'text-cyan-400/80'} leading-tight`}>
                  {log.text}
                </span>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </aside>

      {/* Central 3D Canvas */}
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <HolographicSphere 
            rotation={sphereRotation} 
            scale={sphereScale} 
            position={spherePosition}
            status={status}
          />
        </Canvas>
      </div>

      {/* Central UI Overlays */}
      <div className="relative flex items-center justify-center w-[500px] h-[500px] z-10 pointer-events-none">
        {/* Ring 1: Outer Dashed Ring */}
        <motion.svg
          animate={{ rotate: 360 }}
          transition={{ duration: status === 'listening' ? 10 : 25, repeat: Infinity, ease: "linear" }}
          className={`absolute inset-0 w-full h-full transition-all duration-500 ${status === 'listening' ? 'scale-110 opacity-100' : 'scale-100 opacity-30'}`}
          viewBox="0 0 100 100"
        >
          <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="4 2" className="text-cyan-500" />
        </motion.svg>

        {/* Ring 2: Core containment ring */}
        <motion.svg
          animate={{ rotate: -360 }}
          transition={{ duration: status === 'listening' ? 5 : 15, repeat: Infinity, ease: "linear" }}
          className={`absolute inset-20 w-[calc(100%-10rem)] h-[calc(100%-10rem)] transition-all duration-500 ${status === 'listening' ? 'opacity-100' : 'opacity-20'}`}
          viewBox="0 0 100 100"
        >
          <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="60 40" className="text-cyan-200" />
        </motion.svg>
      </div>

      {/* Live Subtitles Console */}
      <div className="absolute bottom-12 w-full max-w-3xl px-8 z-20">
        <div className="relative bg-black/40 backdrop-blur-md border border-cyan-900/50 rounded-xl p-6 overflow-hidden">
          {/* Decorative corner accents */}
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-cyan-500/50 rounded-tl-xl" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyan-500/50 rounded-tr-xl" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyan-500/50 rounded-bl-xl" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-cyan-500/50 rounded-br-xl" />
          
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-2 h-2 rounded-full ${status === 'speaking' ? 'bg-cyan-400 animate-pulse' : status === 'listening' ? 'bg-red-500 animate-pulse' : 'bg-gray-600'}`} />
            <span className="text-xs font-mono text-cyan-500/70 uppercase tracking-widest">
              {status === 'speaking' ? 'A.R.Y.A. Transmitting' : status === 'listening' ? 'A.R.Y.A. Listening' : 'System Standby'}
            </span>
          </div>
          
          <AnimatePresence mode="wait">
            <motion.p 
              key={subtitle}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-xl md:text-2xl font-light text-cyan-50 tracking-wide leading-relaxed drop-shadow-[0_0_5px_rgba(0,255,255,0.5)]"
            >
              {subtitle}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
