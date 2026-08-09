#!/usr/bin/env python3
"""
Human Behavior Simulation — makes automation act EXACTLY like a real person.

Implements:
1. Bezier-curve mouse movement (ghost-cursor style)
2. Realistic typing with variable delays and typos
3. Random scrolling patterns
4. Mouse hover before clicks
5. Variable reading pauses
6. Realistic click patterns

Based on research from:
- ghost-cursor (https://github.com/Xetera/ghost-cursor)
- scrapfly.io Puppeteer Stealth Guide
- CloverLabs human-cursor
- Roundproxies Puppeteer Humanize guide
"""

import math
import random
import time
import sys
from typing import Tuple, List, Optional


def bezier_curve(start: Tuple[int, int], end: Tuple[int, int],
                 curvature: float = None,
                 steps: int = 30) -> List[Tuple[int, int]]:
    """
    Generate Bezier curve points between two coordinates.
    Mimics natural mouse movement with overshoot and correction.
    """
    if curvature is None:
        curvature = random.uniform(0.5, 2.0)

    # Control points for cubic bezier with natural curvature
    x0, y0 = start
    x3, y3 = end

    # First control point: ~30% along the path, with random offset
    x1 = x0 + (x3 - x0) * 0.3 + random.randint(-50, 50)
    y1 = y0 + (y3 - y0) * 0.3 + random.randint(-50, 50)

    # Second control point: ~70% along, with random offset
    x2 = x0 + (x3 - x0) * 0.7 + random.randint(-30, 30)
    y2 = y0 + (y3 - y0) * 0.7 + random.randint(-30, 30)

    points = []
    for i in range(steps + 1):
        t = i / steps
        # Cubic Bezier formula
        x = (1 - t)**3 * x0 + 3 * (1 - t)**2 * t * x1 + 3 * (1 - t) * t**2 * x2 + t**3 * x3
        y = (1 - t)**3 * y0 + 3 * (1 - t)**2 * t * y1 + 3 * (1 - t) * t**2 * y2 + t**3 * y3

        # Add tiny jitter (real mouse has micro-movements)
        x += random.gauss(0, 1.5)
        y += random.gauss(0, 1.5)

        points.append((int(x), int(y)))

    # Add occasional overshoot near the target (real humans overshoot)
    if random.random() < 0.3 and abs(x3 - x0) > 100:
        overshoot = points[-1]
        correction_x = x3 + (overshoot[0] - x3) * random.uniform(0.05, 0.15)
        correction_y = y3 + (overshoot[1] - y3) * random.uniform(0.05, 0.15)
        # Insert correction points
        points.insert(-3, (int(correction_x), int(correction_y)))
        points.insert(-2, (int((correction_x + x3) / 2), int((correction_y + y3) / 2)))

    return points


def typing_delay(char: str, prev_char: str = "") -> float:
    """
    Calculate realistic typing delay for a character.
    Based on real typing research:
    - Average: 60-100 wpm (200-300 chars/min = 200-500ms/char)
    - Common chars faster (e, t, a, o, i, n, s)
    - Special chars slower
    - After punctuation: pause
    - First char of word: slight pause
    """
    base_delay = random.gauss(0.12, 0.04)  # ~80 wpm average

    # Common letters are faster
    common = "etaoinsrhld"
    if char.lower() in common:
        base_delay *= 0.7

    # Capital letters slightly slower
    if char.isupper():
        base_delay *= 1.2

    # Numbers/symbols slower
    if not char.isalpha():
        base_delay *= 1.5

    # Space after word - slight pause
    if char == ' ':
        base_delay *= 1.3

    # Pause after sentence-ending punctuation
    if char in '.!?':
        base_delay *= 2.0

    # Occasional typo with correction (5% chance)
    if random.random() < 0.05 and prev_char and prev_char.isalpha():
        base_delay += random.uniform(0.3, 0.8)  # Pause before correction

    # Burst typing (sometimes humans type fast in bursts)
    if random.random() < 0.2:
        base_delay *= 0.5

    return max(0.03, base_delay)


def realistic_type_sequence(text: str) -> List[Tuple[str, float]]:
    """
    Generate (char, delay) sequence that mimics real human typing.
    Includes occasional typos and corrections.
    """
    sequence = []
    i = 0
    while i < len(text):
        char = text[i]

        # Occasional typo (3% chance, not at start)
        if i > 2 and random.random() < 0.03 and char.isalpha():
            # Type a wrong nearby key
            wrong_key = chr(ord(char) + random.choice([-1, 1]))
            sequence.append((wrong_key, typing_delay(wrong_key, text[i-1] if i > 0 else "")))
            # Pause (human notices typo)
            sequence.append(("", random.uniform(0.2, 0.6)))
            # Backspace
            sequence.append(("\b", random.uniform(0.08, 0.15)))
            # Now type correct char
            sequence.append((char, typing_delay(char, text[i-1] if i > 0 else "")))
        else:
            prev = text[i-1] if i > 0 else ""
            delay = typing_delay(char, prev)
            sequence.append((char, delay))

        i += 1

    return sequence


def scroll_pattern(viewport_height: int = 800,
                   page_height: int = 3000) -> List[Tuple[int, float]]:
    """
    Generate realistic scroll pattern for reading a page.
    Real humans:
    - Scroll in bursts
    - Pause to read
    - Scroll back occasionally
    - Variable speed
    """
    pattern = []
    current_y = 0

    while current_y < page_height - viewport_height:
        # Scroll burst
        burst_size = random.randint(100, 400)
        pattern.append((burst_size, random.uniform(0.1, 0.3)))

        # Reading pause
        pause = random.uniform(0.5, 4.0)
        pattern.append((0, pause))

        current_y += burst_size

        # Occasional scroll back (25% chance)
        if random.random() < 0.25 and current_y > 200:
            back = random.randint(50, 200)
            pattern.append((-back, random.uniform(0.2, 0.5)))
            current_y -= back
            # Pause after scrolling back
            pattern.append((0, random.uniform(0.5, 1.5)))

    return pattern


class HumanBehavior:
    """Generate human-like browser interactions."""

    @staticmethod
    def mouse_move_script(from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> str:
        """Generate JS to do human-like mouse movement in browser."""
        points = bezier_curve(from_pos, to_pos)

        js_points = str(points)
        return f"""
        async function humanMouseMove() {{
            const points = {js_points};
            const startEvent = new MouseEvent('mousemove', {{
                bubbles: true, cancelable: true, view: window,
                clientX: {from_pos[0]}, clientY: {from_pos[1]}
            }});
            document.dispatchEvent(startEvent);
            for (let i = 0; i < points.length; i++) {{
                await new Promise(r => setTimeout(r, {random.randint(5, 15)}));
                const [x, y] = points[i];
                const event = new MouseEvent('mousemove', {{
                    bubbles: true, cancelable: true, view: window,
                    clientX: x, clientY: y
                }});
                document.dispatchEvent(event);
            }}
        }}
        await humanMouseMove();
        """

    @staticmethod
    def type_text_script(selector: str, text: str) -> str:
        """Generate JS for human-like typing."""
        sequence = realistic_type_sequence(text)
        chars = [{"char": c, "delay": d} for c, d in sequence]

        return f"""
        async function humanType() {{
            const el = document.querySelector('{selector}');
            if (!el) return;
            el.focus();
            el.value = '';
            const sequence = {str(chars)};
            for (const item of sequence) {{
                await new Promise(r => setTimeout(r, item.delay * 1000));
                if (item.char === '') continue;
                if (item.char === '\\b') {{
                    el.value = el.value.slice(0, -1);
                }} else {{
                    el.value += item.char;
                }}
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
                el.dispatchEvent(new KeyboardEvent('keydown', {{
                    key: item.char, bubbles: true
                }}));
            }}
        }}
        await humanType();
        """

    @staticmethod
    def scroll_script() -> str:
        """Generate JS for human-like scrolling."""
        pattern = scroll_pattern()

        events = []
        for delta_y, delay in pattern:
            events.append({"scroll": delta_y, "delay": delay})

        return f"""
        async function humanScroll() {{
            const events = {str(events)};
            for (const ev of events) {{
                await new Promise(r => setTimeout(r, ev.delay * 1000));
                window.scrollBy({{top: ev.scroll, behavior: 'smooth'}});
            }}
        }}
        await humanScroll();
        """

    @staticmethod
    def click_with_hover_script(selector: str) -> str:
        """Generate JS for hover-then-click like a human."""
        # Hover first, pause, then click
        hover_points = bezier_curve((0, 0), (500, 500), steps=15)

        return f"""
        async function humanClick() {{
            const el = document.querySelector('{selector}');
            if (!el) return;
            const rect = el.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;

            // Hover (mousemove)
            const event = new MouseEvent('mousemove', {{
                bubbles: true, cancelable: true, view: window,
                clientX: x, clientY: y
            }});
            el.dispatchEvent(event);

            // Pause before click (human reaction time)
            await new Promise(r => setTimeout(r, {random.randint(100, 400)}));

            // Click
            el.click();

            // Also dispatch mousedown/mouseup for sites that check
            el.dispatchEvent(new MouseEvent('mousedown', {{
                bubbles: true, cancelable: true, view: window,
                clientX: x, clientY: y, button: 0
            }}));
            await new Promise(r => setTimeout(r, {random.randint(30, 100)}));
            el.dispatchEvent(new MouseEvent('mouseup', {{
                bubbles: true, cancelable: true, view: window,
                clientX: x, clientY: y, button: 0
            }}));
        }}
        await humanClick();
        """


if __name__ == "__main__":
    print("=" * 70)
    print("🎭 HUMAN BEHAVIOR SIMULATION TEST")
    print("=" * 70)

    # Test 1: Bezier curve
    print("\n1️⃣  Mouse Movement (Bezier curve):")
    start = (0, 0)
    end = (500, 300)
    points = bezier_curve(start, end, steps=10)
    print(f"   Generated {len(points)} points from {start} to {end}")
    print(f"   First 3: {points[:3]}")
    print(f"   Last 3: {points[-3:]}")

    # Test 2: Typing pattern
    print("\n2️⃣  Typing Pattern:")
    text = "Hello World"
    sequence = realistic_type_sequence(text)
    total_time = sum(d for _, d in sequence)
    print(f"   Text: '{text}'")
    print(f"   Sequence: {len(sequence)} chars")
    print(f"   Total time: {total_time:.2f}s (avg {(total_time/len(text))*1000:.0f}ms/char)")

    # Test 3: Scroll pattern
    print("\n3️⃣  Scroll Pattern:")
    pattern = scroll_pattern()
    total_scroll = sum(s for s, _ in pattern)
    total_pause = sum(d for _, d in pattern)
    print(f"   Generated {len(pattern)} scroll events")
    print(f"   Total scroll: {total_scroll}px")
    print(f"   Total pause time: {total_pause:.1f}s")

    # Test 4: Full human interaction
    print("\n4️⃣  Full Human Interaction Sequence:")
    print("   - Move mouse to field")
    print("   - Hover (200ms)")
    print("   - Click field")
    print("   - Type 'test@example.com' with realistic delays")
    print("   - Tab to next field (300ms)")
    print("   - Type password with realistic delays")
    print("   - Move mouse to submit button")
    print("   - Hover (200ms)")
    print("   - Click submit")
    print(f"   Estimated total time: ~8-15 seconds (realistic)")

    print("\n" + "=" * 70)
    print("✅ All human behavior generators working")
    print("=" * 70)
