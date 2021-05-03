import unittest
from os.path import abspath, dirname, join

from pysimpleplotter import PySimplePlotter, WindowKey


class TestFileInput(unittest.TestCase):
    def setUp(self):
        self.psp = PySimplePlotter()
        self.data_dir = join(dirname(abspath(__file__)), "data")

    def test_load_horiba_raman(self) -> None:
        window = self.psp.window()
        event, values = window.read(timeout=0)

        # Mock input
        values[WindowKey.FILE_NAME] = join(self.data_dir, "Horiba_Raman.txt")

        # Test
        self.psp.load(window, event, values)
        self.assertListEqual(
            list(self.psp.dfs[0].columns),
            [f"col{i+1}" for i in range(2)],
        )
        self.assertEqual(len(self.psp.dfs[0]), 830)
        window.close()

    def test_load_ir_spectrum(self) -> None:
        window = self.psp.window()
        event, values = window.read(timeout=0)

        # Mock input
        values[WindowKey.FILE_NAME] = join(self.data_dir, "IR_Spectrum.txt")

        # Test
        self.psp.load(window, event, values)
        self.assertListEqual(
            list(self.psp.dfs[0].columns),
            [f"col{i+1}" for i in range(2)],
        )
        self.assertEqual(len(self.psp.dfs[0]), 1713)
        window.close()

    def test_load_labview_absorption(self) -> None:
        window = self.psp.window()
        event, values = window.read(timeout=0)

        # Mock input
        values[WindowKey.FILE_NAME] = join(self.data_dir, "LabView_Absorption.txt")

        # Test
        self.psp.load(window, event, values)
        self.assertListEqual(
            list(self.psp.dfs[0].columns),
            [f"col{i+1}" for i in range(4)],
        )
        self.assertEqual(len(self.psp.dfs[0]), 401)
        window.close()

    def test_load_labview_diffuse_reflectance(self) -> None:
        window = self.psp.window()
        event, values = window.read(timeout=0)

        # Mock input
        values[WindowKey.FILE_NAME] = join(
            self.data_dir, "LabView_DiffuseReflectance.txt"
        )

        # Test
        self.psp.load(window, event, values)
        self.assertListEqual(
            list(self.psp.dfs[0].columns),
            [f"col{i+1}" for i in range(4)],
        )
        self.assertEqual(len(self.psp.dfs[0]), 201)
        window.close()

    def test_load_luminescence(self) -> None:
        window = self.psp.window()
        event, values = window.read(timeout=0)

        # Mock input
        values[WindowKey.FILE_NAME] = join(self.data_dir, "Luminescence.txt")

        # Test
        self.psp.load(window, event, values)
        self.assertListEqual(
            list(self.psp.dfs[0].columns),
            [f"col{i+1}" for i in range(2)],
        )
        self.assertEqual(len(self.psp.dfs[0]), 1024)
        window.close()

    def test_load_named_luminescence(self) -> None:
        window = self.psp.window()
        event, values = window.read(timeout=0)

        # Mock input
        values[WindowKey.FILE_NAME] = join(self.data_dir, "Named_Luminescence.txt")

        # Test
        self.psp.load(window, event, values)
        self.assertListEqual(
            list(self.psp.dfs[0].columns),
            ["x_col", "y_col"],
        )
        self.assertEqual(len(self.psp.dfs[0]), 1025)
        window.close()

    def test_load_perkin_elmer_tga(self) -> None:
        window = self.psp.window()
        event, values = window.read(timeout=0)

        # Mock input
        values[WindowKey.FILE_NAME] = join(self.data_dir, "PerkinElmer_TGA.txt")

        # Test
        self.psp.load(window, event, values)
        self.assertListEqual(
            list(self.psp.dfs[0].columns),
            [f"col{i+1}" for i in range(6)],
        )
        self.assertEqual(len(self.psp.dfs[0]), 5573)
        window.close()


if __name__ == "__main__":
    unittest.main()
