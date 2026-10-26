"use client";

import { useEffect, useRef, useState } from "react";
import { animate } from "motion/react";

// Counts a number up from 0 the first time, then from the old value to the new one
export default function CountUp({ value, decimals = 0 }: { value: number; decimals?: number }) {
  const [display, setDisplay] = useState(0);
  const previous = useRef(0);

  useEffect(() => {
    const controls = animate(previous.current, value, {
      duration: 0.8,
      ease: "easeOut",
      onUpdate: (v) => setDisplay(v),
    });
    previous.current = value;
    return () => controls.stop();
  }, [value]);

  return <>{display.toFixed(decimals)}</>;
}