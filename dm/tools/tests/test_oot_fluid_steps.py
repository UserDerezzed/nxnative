"""Ocarina of Time's fluid simulation steps (the water's ripples): the game takes the whole part of the frame's step as its update count, so a frame shorter than 1/60 s
(the fractional step at 120 fps: 0.5) gave it none and the ripples froze. The stub carries the part under a whole step to the next frame, per simulation instance, leaves
a step of 1 or more as the game takes it, and on a frame where the grid's origin moved runs the update at once (taken from the next one): the grid's scroll is part of an
update and holds for that frame only. The emitted words run here on a small interpreter of the instruction forms the stub uses (no emulator needed)."""
import importlib
import importlib.util
import math
from pathlib import Path
import re
import struct
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'dm/tools'))

spec = importlib.util.spec_from_file_location('oot_fluid', REPO / 'dm/games/0400486024DEC000/patches.py')
assert spec is not None and spec.loader is not None
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)
try:
    capstone = importlib.import_module('capstone')
except ImportError:
    capstone = None

AREA, STATE, FLUID = 0x800000, 0x900000, 0x472e0
SITE = FLUID + 0x318
N = r'#(0x[0-9a-f]+|\d+)'   # an immediate as Capstone prints it
THIS, INSTANCES, STACK = 0x10000, 0x20000, 0x40000   # the fluid object (x21; its instances' array at +0x28, the grid's origin at +0xab0), that array, and sp
ORIGIN = (-31 & 0xffffffff) << 32 | (-27 & 0xffffffff)   # the origin's two words, in metres

def emitted(others=None):
    """The stub's words, the sites it asserted and the words it put at them"""
    words, sites, puts = [], {}, {}
    ctx = SimpleNamespace(state=STATE, others={'fluid simulation': FLUID} if others is None else others, here=lambda: AREA + 4 * len(words), emit=words.append,
                          site=lambda off, orig: sites.__setitem__(off, orig), put=lambda off, ws, why: puts.__setitem__(off, (ws, why)))
    profile.fluid_steps(ctx)
    return words, sites, puts


def fcvtzs(v, bits=0):   # to a signed 32-bit integer, toward zero, saturating; NaN is 0
    if math.isnan(v): return 0
    return int(max(-2 ** 31, min(2 ** 31 - 1, math.trunc(v * 2 ** bits))))


class Machine:
    """The instruction forms the stub may use, read from Capstone's text; any other instruction fails the test"""
    def __init__(self, words):
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        self.code = {i.address: (i.mnemonic, i.op_str) for i in md.disasm(b''.join(struct.pack('<I', w) for w in words), AREA)}
        assert len(self.code) == len(words), 'a word Capstone does not decode'
        self.mem = {THIS + 0x28: INSTANCES, THIS + 0xab0: ORIGIN}   # 8-byte and 4-byte cells by address
        self.writes = []
        for k in range(3): self.run(1.0, instance=k)   # each instance has seen the origin
        self.writes.clear()

    def move(self, metres=1):
        """The grid's origin moves: the frame drawn next is the one whose update scrolls the grid"""
        self.mem[THIS + 0xab0] += metres

    def run(self, step, instance=0):
        """One pass through the stub with s0 = step and x23 = that instance: the count in w9"""
        M64 = 0xffffffffffffffff
        x = {n: 0x100000000000 + n for n in range(31)}
        x[21], x[23], x[31] = THIS, INSTANCES + instance * 0x8b8, STACK
        before, pc, n, flags = dict(x), AREA, 0, None
        cond = lambda c, f: {'eq': f[1], 'ne': not f[1], 'lt': f[0] != f[3], 'ge': f[0] == f[3]}[c]
        def subs(a, b, bits):   # the flags (N, Z, C, V) of a - b
            m = (1 << bits) - 1; a &= m; b &= m; d = (a - b) & m; s = 1 << (bits - 1)
            return bool(d & s), d == 0, a >= b, bool((a ^ b) & (a ^ d) & s)
        while pc in self.code:
            n += 1; assert n < 60, 'the stub does not return'
            m, ops = self.code[pc]; t = f'{m} {ops}'; nxt = pc + 4
            def r(name):
                if name == 'sp': return x[31]
                if name in ('wzr', 'xzr'): return 0
                k = int(name[1:]); return x[k] & (0xffffffff if name[0] == 'w' else M64)
            def w(name, v):
                if name == 'sp': x[31] = v & M64; return
                k = int(name[1:]); x[k] = v & (0xffffffff if name[0] == 'w' else M64)
            def store(a, v, size):
                self.mem[a] = v
                if not STACK - 0x100 <= a < STACK: self.writes.append((a, size))
            if g := re.fullmatch(rf'adrp (x\d+), {N}', t): w(g[1], int(g[2], 0))
            elif g := re.fullmatch(r'fcvtzs (w\d+), s0', t): w(g[1], fcvtzs(step))
            elif g := re.fullmatch(rf'fcvtzs (w\d+), s0, {N}', t): w(g[1], fcvtzs(step, int(g[2], 0)))
            elif g := re.fullmatch(rf'cbnz (w\d+), {N}', t): nxt = int(g[2], 0) if r(g[1]) else nxt
            elif g := re.fullmatch(rf'tbnz (w\d+), {N}, {N}', t): nxt = int(g[3], 0) if r(g[1]) >> int(g[2], 0) & 1 else nxt
            elif g := re.fullmatch(rf'stp (x\d+), (x\d+), \[sp, #-(0x[0-9a-f]+|\d+)\]!', t):
                w('sp', r('sp') - int(g[3], 0)); store(r('sp'), r(g[1]), 8); store(r('sp') + 8, r(g[2]), 8)
            elif g := re.fullmatch(rf'ldp (x\d+), (x\d+), \[sp\], {N}', t):
                w(g[1], self.mem[r('sp')]); w(g[2], self.mem[r('sp') + 8]); w('sp', r('sp') + int(g[3], 0))
            elif g := re.fullmatch(rf'ldr ([xw]\d+), \[(x\d+), {N}\]', t): w(g[1], self.mem.get(r(g[2]) + int(g[3], 0), 0))
            elif g := re.fullmatch(rf'and (w\d+), (w\d+), {N}', t): w(g[1], r(g[2]) & int(g[3], 0))
            elif g := re.fullmatch(rf'lsr (w\d+), (w\d+), {N}', t): w(g[1], r(g[2]) >> int(g[3], 0))
            elif g := re.fullmatch(rf'str ([xw]\d+), \[(x\d+), {N}\]', t): store(r(g[2]) + int(g[3], 0), r(g[1]), 8 if g[1][0] == 'x' else 4)
            elif g := re.fullmatch(r'sub (x\d+), (x\d+), (x\d+)', t): w(g[1], r(g[2]) - r(g[3]))
            elif g := re.fullmatch(rf'sub (w\d+), (w\d+), {N}, lsl #12', t): w(g[1], r(g[2]) - (int(g[3], 0) << 12))
            elif g := re.fullmatch(rf'ubfx (x\d+), (x\d+), {N}, {N}', t): w(g[1], r(g[2]) >> int(g[3], 0) & ((1 << int(g[4], 0)) - 1))
            elif g := re.fullmatch(rf'add (x\d+), (x\d+), (x\d+), lsl {N}', t): w(g[1], r(g[2]) + (r(g[3]) << int(g[4], 0)))
            elif g := re.fullmatch(r'add (w\d+), (w\d+), (w\d+)', t): w(g[1], r(g[2]) + r(g[3]))
            elif g := re.fullmatch(r'eor (x\d+), (x\d+), (x\d+)', t): w(g[1], r(g[2]) ^ r(g[3]))
            elif g := re.fullmatch(rf'cmp (w\d+), {N}, lsl #12', t): flags = subs(r(g[1]), int(g[2], 0) << 12, 32)
            elif g := re.fullmatch(rf'ccmp (x\d+), {N}, {N}, (\w+)', t):
                v = int(g[3], 0); flags = subs(r(g[1]), int(g[2], 0), 64) if cond(g[4], flags) else (bool(v & 8), bool(v & 4), bool(v & 2), bool(v & 1))
            elif g := re.fullmatch(r'cset (w\d+), (\w+)', t): w(g[1], int(cond(g[2], flags)))
            elif g := re.fullmatch(r'csel (w\d+), (w\d+), (w\d+), (\w+)', t): w(g[1], r(g[2]) if cond(g[4], flags) else r(g[3]))
            elif g := re.fullmatch(rf'b {N}', t): nxt = int(g[1], 0)
            else: raise AssertionError(f'the stub uses an instruction this test does not know: {t}')
            pc = nxt
        assert pc == SITE + 4, f'the stub leaves to {pc:#x}, not the instruction after its site'
        changed = {k for k in x if x[k] != before[k]}
        assert changed <= {9, 16, 17}, f'registers other than x9, x16, x17 changed (31 is sp): {sorted(changed)}'
        count = x[9] & 0xffffffff
        return count - (1 << 32) if count >> 31 else count

    def parts(self):   # the writes to the carried parts (state +0x188, a word per instance in 8-byte cells)
        return [a for a, size in self.writes if STATE + 0x188 <= a < STATE + 0x1a8]


@unittest.skipIf(capstone is None, 'capstone, the rewriter disassembler')
class FluidSteps(unittest.TestCase):
    def machine(self):
        words, sites, puts = emitted()
        self.assertEqual(sites, {SITE: '0900381e'})   # fcvtzs w9, s0
        self.assertEqual(list(puts), [SITE])
        self.assertEqual(puts[SITE][0], [profile.B(SITE, AREA)])
        return Machine(words)

    def test_a_whole_step_or_more_is_the_games_count(self):
        m = self.machine()
        for step, count in ((1.0, 1), (2.0, 2), (3.0, 3), (1.3, 1), (2.9, 2), (1.3, 1), (1.3, 1), (1.3, 1)):
            with self.subTest(step=step):
                m.move(); self.assertEqual(m.run(step), count)
        self.assertEqual(m.parts(), [], 'a step of 1 or more carries nothing, whether the grid moved or not')

    def test_half_steps_update_every_other_frame(self):
        m = self.machine()
        counts = [m.run(0.5) for _ in range(120)]
        self.assertEqual(counts[:6], [0, 1, 0, 1, 0, 1])
        self.assertEqual(sum(counts), 60)

    def test_any_step_under_one_keeps_real_time(self):
        for fps in (70, 90, 100, 119):
            with self.subTest(fps=fps):
                m = self.machine()
                counts = [m.run(60 / fps) for _ in range(fps * 10)]   # ten seconds of frames
                self.assertLessEqual(set(counts), {0, 1})
                self.assertAlmostEqual(sum(counts), 600, delta=1)

    def test_a_move_of_the_grid_updates_in_its_own_frame(self):
        """The grid's scroll holds for the frame its origin moved in: that frame updates even when none is due, and the next update due is the one it took"""
        m = self.machine()
        self.assertEqual([m.run(0.5) for _ in range(4)], [0, 1, 0, 1])
        m.move()
        self.assertEqual(m.run(0.5), 1, 'the frame of the move updates')
        self.assertEqual([m.run(0.5) for _ in range(5)], [0, 0, 1, 0, 1], 'the update it took is not run again')
        m = self.machine()
        counts = []
        for frame in range(1200):   # ten seconds at 120 with the origin moving five times a second, on frames with and without an update due
            if frame % 24 in (5, 6): m.move()
            counts.append(m.run(0.5))
            if frame % 24 in (5, 6): self.assertEqual(counts[-1], 1)
        self.assertLessEqual(set(counts), {0, 1})
        self.assertAlmostEqual(sum(counts), 600, delta=1)

    def test_each_instance_carries_its_own_part_and_sees_the_move(self):
        m = self.machine()
        totals = [0, 0, 0]
        for frame in range(120):
            if frame == 60: m.move()
            for k in range(3):
                c = m.run(0.5, instance=k); totals[k] += c
                if frame == 60: self.assertEqual(c, 1)
        self.assertEqual(totals, [60, 60, 60])
        self.assertEqual(len(set(m.parts())), 3)
        self.assertTrue(all(STATE + 0x188 <= a < STATE + 0x1c8 for a, _ in m.writes), 'four parts at state +0x188 and four origins at +0x1a8, clear of the frame count (+0x180) and +0x200')

    def test_no_step_and_bad_steps_give_none(self):
        m = self.machine()
        self.assertEqual([m.run(0.0) for _ in range(5)], [0] * 5)
        self.assertEqual(m.run(0.75), 0)
        self.assertEqual(m.run(-0.5), 0)                    # nothing taken back
        self.assertEqual(m.run(float('nan')), 0)
        self.assertEqual(m.run(0.25), 1)                    # 0.75 + 0.25
        self.assertEqual(m.run(-3.0), -3)                   # as the game's own conversion

    def test_a_build_without_the_function_gets_no_stub(self):
        self.assertEqual(emitted({'fluid simulation': None}), ([], {}, {}))
        self.assertEqual(emitted({}), ([], {}, {}))


class Wiring(unittest.TestCase):
    def test_both_frame_step_stubs_place_it(self):
        for enabled in (False, True):
            ctx = SimpleNamespace(experimental_fractional=enabled, build_id=profile.fractional_build, base=0x6e6be0, state=STATE, others={},
                                  here=lambda: AREA, emit=Mock(), site=Mock(), put=Mock())
            with patch.object(profile, 'real_speed'), patch.object(profile, 'dynamic_resolution'), patch.object(profile, 'heap_retry', create=True), \
                    patch.object(profile, 'fluid_steps') as fluid:
                profile.frame_step(ctx)
                fluid.assert_called_once_with(ctx)

    def test_the_rule_names_the_function(self):
        rule = profile.MATCH_FRAME_STEP['main'][0]
        self.assertEqual(rule['others']['fluid simulation'], {'size': 0x4854, 'fingerprints': ['d70f5d41951d4fcd0a5fc8fc2c8aeebdba0993ef439565927eaea8dbc0d7ca8d']})


if __name__ == '__main__':
    unittest.main()
