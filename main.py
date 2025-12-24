#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
3D Particle Collision Generator - Enhanced Version
"""

import sys
import os
import warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.filterwarnings('ignore')

def main():
    """Main entry point"""
    try:
        os.makedirs("output", exist_ok=True)
        os.makedirs("config", exist_ok=True)

        try:
            import pygame
            pygame.init()
        except:
            pass

        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)

        from src.ui.enhanced_dashboard import EnhancedDashboard
        dashboard = EnhancedDashboard()
        dashboard.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

