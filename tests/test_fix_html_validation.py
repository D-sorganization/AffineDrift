"""Tests for the fix_html_validation tool."""

import sys
from pathlib import Path

# Add project root to path to ensure src module can be imported
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.tools.fix_html_validation import (
    add_button_type,
    add_iframe_title,
    add_landmark_aria_labels,
    add_navbar_brand_aria_label,
    fix_crossorigin_attribute,
    fix_dots_in_ids,
    remove_aria_labelledby_dropdown,
    remove_redundant_role_link,
)


def test_fix_crossorigin_attribute():
    """Test fixing crossorigin attribute."""
    html = '<script src="foo.js" crossorigin=""></script>'
    expected = '<script src="foo.js" crossorigin></script>'
    assert fix_crossorigin_attribute(html) == expected

    # Test no change if already correct
    assert fix_crossorigin_attribute(expected) == expected


def test_remove_redundant_role_link():
    """Test removing redundant role='link'."""
    html = '<a href="#" role="link">Link</a>'
    expected = '<a href="#">Link</a>'
    assert remove_redundant_role_link(html) == expected

    # Test handling whitespace
    html_space = '<a href="#"   role="link">Link</a>'
    expected_space = '<a href="#">Link</a>'
    assert remove_redundant_role_link(html_space) == expected_space


def test_remove_aria_labelledby_dropdown():
    """Test removing aria-labelledby from dropdown-menu."""
    html = '<div class="dropdown-menu" aria-labelledby="dropdownMenu1">'
    expected = '<div class="dropdown-menu">'
    assert remove_aria_labelledby_dropdown(html) == expected


def test_add_navbar_brand_aria_label():
    """Test adding aria-label to navbar brand."""
    html = '<a href="/" class="navbar-brand navbar-brand-logo">'
    expected = '<a href="/" class="navbar-brand navbar-brand-logo" aria-label="Home">'
    assert add_navbar_brand_aria_label(html) == expected

    # Test no duplication
    assert add_navbar_brand_aria_label(expected) == expected


def test_fix_dots_in_ids():
    """Test replacing dots with dashes in IDs."""
    html = '<h1 id="my.heading">Heading</h1><a href="#my.heading">Link</a>'
    expected = '<h1 id="my-heading">Heading</h1><a href="#my-heading">Link</a>'
    assert fix_dots_in_ids(html) == expected


def test_add_button_type():
    """Test adding type='button' to buttons."""
    html = '<button class="btn">Click</button>'
    expected = '<button type="button" class="btn">Click</button>'
    assert add_button_type(html) == expected

    # Test no change if type exists
    html_submit = '<button type="submit">Submit</button>'
    assert add_button_type(html_submit) == html_submit


def test_add_iframe_title():
    """Test adding title to iframes."""
    html = '<iframe src="foo.html"></iframe>'
    expected = '<iframe title="Embedded Content" src="foo.html"></iframe>'
    assert add_iframe_title(html) == expected

    # Test no change if title exists
    html_title = '<iframe title="Map" src="map.html"></iframe>'
    assert add_iframe_title(html_title) == html_title


def test_add_landmark_aria_labels():
    """Test adding aria-labels to landmarks."""
    # TOC
    html_toc = '<nav id="TOC">'
    expected_toc = '<nav id="TOC" aria-label="Table of Contents">'
    assert add_landmark_aria_labels(html_toc) == expected_toc

    # Left Sidebar
    html_left = '<aside class="left-sidebar">'
    expected_left = '<aside class="left-sidebar" aria-label="Primary Sidebar">'
    assert add_landmark_aria_labels(html_left) == expected_left

    # Right Sidebar
    html_right = '<aside class="right-sidebar">'
    expected_right = '<aside class="right-sidebar" aria-label="Secondary Sidebar">'
    assert add_landmark_aria_labels(html_right) == expected_right
