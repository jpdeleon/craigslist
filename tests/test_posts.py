# -*- coding: utf-8 -*-
import sys
import subprocess

sys.path.append("..")


def test_init():
    """CLI"""
    _ = subprocess.Popen(
        ["./posts.py", "-g"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
