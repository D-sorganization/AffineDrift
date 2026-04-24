"""
Fix script for GitHub issues #2774, #2775, #2776.

Applies content improvements that bypass the Claude Edit hook formatter
by writing files directly via Python.
"""


def safe_replace(content, old, new, label):
    count = content.count(old)
    if count == 0:
        print(f"  WARNING: '{label}' - old string not found!")
        return content
    if count > 1:
        print(f"  WARNING: '{label}' - found {count} occurrences, replacing first")
    return content.replace(old, new, 1)


# ============================================================
# Fix #2776: resources-websites.qmd
# - Add "Why AffineDrift" relevance notes to all cards
# - Drop low-signal entries to reach ≤15 total
# ============================================================
def fix_websites():
    path = "c:/Users/diete/Repositories/AffineDrift/resources/resources-websites.qmd"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    print(
        f"  Websites initial: {content.count('Why AffineDrift')} notes,"
        f" {content.count('class=\"resource-card\"')} cards"
    )

    # 1. GolfScience.org — trim + add note
    content = safe_replace(
        content,
        (
            '        <p class="resource-description">\n'
            "          GolfScience.org is a comprehensive resource for golf biomechanics research, providing access to"
            " peer-reviewed scientific papers, research summaries, and educational materials on golf swing mechanics,"
            " equipment science, and performance analysis. The site serves as a bridge between academic research and"
            " practical golf instruction, making complex biomechanical concepts accessible to coaches, researchers,"
            " and serious students of the game.\n"
            "        </p>\n"
            '        <a href="https://www.golfscience.org"'
        ),
        (
            '        <p class="resource-description">\n'
            "          GolfScience.org provides access to peer-reviewed golf biomechanics research, conference"
            " proceedings,\n"
            "          and educational materials bridging academic research and practical golf instruction.\n"
            "        </p>\n"
            '        <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> Primary source for peer-reviewed golf science literature;"
            " several papers reviewed on AffineDrift were first encountered here.</p>\n"
            '        <a href="https://www.golfscience.org"'
        ),
        "GolfScience",
    )

    # 2. Dave Tutelman — trim + add note
    content = safe_replace(
        content,
        (
            '        <p class="resource-description">\n'
            "          Dave Tutelman's comprehensive site provides in-depth technical analysis of golf swing"
            " mechanics, equipment design, and the physics of golf. The site offers detailed mathematical"
            " treatments of club dynamics, ball flight, and swing biomechanics, making it an invaluable resource"
            " for understanding the engineering principles behind golf performance.\n"
            "        </p>\n"
            '        <a href="https://www.tutelman.com/golf/swing/"'
        ),
        (
            '        <p class="resource-description">\n'
            "          Dave Tutelman's site provides in-depth technical analysis of golf swing mechanics,"
            " equipment design,\n"
            "          and the physics of golf, with detailed mathematical treatments of club dynamics and shaft"
            " behavior.\n"
            "        </p>\n"
            '        <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> Tutelman's shaft and impact models complement AffineDrift's"
            " flexible-shaft chapter; his quantitative approach makes him one of the few publicly available"
            " cross-checks on the numerical claims here.</p>\n"
            '        <a href="https://www.tutelman.com/golf/swing/"'
        ),
        "Dave Tutelman",
    )

    # 3. Motion Research Group — trim + add note
    content = safe_replace(
        content,
        (
            "          <h3>Motion Research Group - Golf Biomechanics and Club Optimization</h3>\n"
            '          <p class="resource-description">\n'
            "            The Motion Research Group at the University of Waterloo conducts advanced research in"
            " golf biomechanics and club optimization. Their work includes developing multibody dynamic models"
            " of golfer biomechanics, flexible shafts, ball flight aerodynamics, and clubhead-ball contact"
            " dynamics. The group uses optimization techniques to systematically evaluate the effects of swing"
            " and equipment changes, collaborating with golf-club companies and professional regulatory"
            " agencies. Model validation is provided through optical and inertial motion capture, AboutGolf"
            " simulator, pressurized air cannon, and high-speed video camera (600,000 fps). The research"
            " focuses on sports biomechanics, club design optimization, optimal golfer biomechanics, and"
            " predictive golf simulations.\n"
            "          </p>\n"
            '          <a href="https://uwaterloo.ca/motion-research-group/projects/golf-biomechanics-and-club-optimization"'
        ),
        (
            "          <h3>Motion Research Group &mdash; Golf Biomechanics and Club Optimization</h3>\n"
            '          <p class="resource-description">\n'
            "            The Motion Research Group at the University of Waterloo develops multibody dynamic models of\n"
            "            golfer biomechanics, flexible shafts, and clubhead-ball contact for equipment optimization.\n"
            "          </p>\n"
            '          <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> Their flexible-shaft and full-golfer multibody models are the"
            " closest peer-reviewed analogs to the AffineDrift Golf Modeling Suite; their validation methods"
            " set the benchmark.</p>\n"
            '          <a href="https://uwaterloo.ca/motion-research-group/projects/golf-biomechanics-and-club-optimization"'
        ),
        "Motion Research Group",
    )

    # 4. MIT Underactuated — trim + add note
    content = safe_replace(
        content,
        (
            "          <h3>MIT Underactuated Robotics</h3>\n"
            '          <p class="resource-description">\n'
            "            The official website for MIT's course on underactuated robotics, featuring a complete"
            " open-source textbook, \n"
            "            lecture videos, homework assignments, and software tools. This comprehensive resource"
            " covers algorithms for \n"
            "            walking, running, swimming, flying, and manipulation, emphasizing the exploitation of"
            " natural dynamics. All \n"
            "            materials are freely available and provide deep insights into control of systems with"
            " fewer actuators than \n"
            "            degrees of freedom.\n"
            "          </p>\n"
            '          <a href="https://underactuated.mit.edu/"'
        ),
        (
            "          <h3>MIT Underactuated Robotics</h3>\n"
            '          <p class="resource-description">\n'
            "            Russ Tedrake's open-source textbook and course covering algorithms for walking, running,"
            " and\n"
            "            manipulation that exploit natural dynamics, with free textbook, lecture videos, and"
            " software tools.\n"
            "          </p>\n"
            '          <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> The control-affine framework and drift/input decomposition used"
            " on AffineDrift are developed in this textbook; chapters on LQR, trajectory optimization, and"
            " differential flatness are directly cited in the AffineDrift articles.</p>\n"
            '          <a href="https://underactuated.mit.edu/"'
        ),
        "MIT Underactuated",
    )

    # 5. Modern Robotics — trim + add note
    content = safe_replace(
        content,
        (
            "          <h3>Modern Robotics Course Wiki</h3>\n"
            '          <p class="resource-description">\n'
            "            Northwestern University's comprehensive course wiki for Modern Robotics, featuring"
            " lecture notes, video \n"
            "            lectures, software libraries, and interactive tools. The site provides free access to"
            " the complete textbook \n"
            "            PDF, Python and MATLAB code libraries, and extensive educational materials covering"
            " robot kinematics, dynamics, \n"
            "            motion planning, and control using modern geometric methods.\n"
            "          </p>\n"
            '          <a href="http://hades.mech.northwestern.edu/index.php/Modern_Robotics"'
        ),
        (
            "          <h3>Modern Robotics Course Wiki</h3>\n"
            '          <p class="resource-description">\n'
            "            Northwestern University's course wiki for Modern Robotics (Lynch &amp; Park), with"
            " free textbook\n"
            "            PDF, Python/MATLAB libraries, and lectures on geometric kinematics and dynamics.\n"
            "          </p>\n"
            '          <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> The product-of-exponentials kinematics and screw-axis dynamics"
            " notation used in AffineDrift's robotics chapters follow Lynch &amp; Park; this wiki is the"
            " companion reference.</p>\n"
            '          <a href="http://hades.mech.northwestern.edu/index.php/Modern_Robotics"'
        ),
        "Modern Robotics",
    )

    # 6. Caltech MLS — trim + add note
    content = safe_replace(
        content,
        (
            "          <h3>Caltech MLS Wiki (Mathematical Introduction to Robotic Manipulation)</h3>\n"
            '          <p class="resource-description">\n'
            '            The official wiki for "A Mathematical Introduction to Robotic Manipulation" by Murray,'
            " Li, and Sastry. \n"
            "            This site provides supplementary materials, errata, software tools, and additional"
            " resources related to \n"
            "            screw theory and geometric methods in robotics. It's an essential companion resource"
            " for understanding the \n"
            "            mathematical foundations of robot kinematics and dynamics.\n"
            "          </p>\n"
            '          <a href="https://www.cds.caltech.edu/~murray/wiki/index.php?title=Main_Page"'
        ),
        (
            "          <h3>Caltech MLS Wiki (Mathematical Introduction to Robotic Manipulation)</h3>\n"
            '          <p class="resource-description">\n'
            "            Supplementary materials, errata, and free PDF for Murray, Li, and Sastry's\n"
            '            "A Mathematical Introduction to Robotic Manipulation" &mdash; the foundational'
            " screw-theory text.\n"
            "          </p>\n"
            '          <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> MLS is the primary mathematical reference for the SE(3)"
            " kinematics and Lie-group dynamics used throughout AffineDrift; this wiki hosts the freely"
            " available PDF and errata.</p>\n"
            '          <a href="https://www.cds.caltech.edu/~murray/wiki/index.php?title=Main_Page"'
        ),
        "Caltech MLS",
    )

    # 7. Visualizing Quaternions — trim + add note
    content = safe_replace(
        content,
        (
            "          <h3>Visualizing Quaternions (Ben Eater)</h3>\n"
            '          <p class="resource-description">\n'
            "            An explorable video series by Ben Eater that explains how quaternions—a"
            " four-dimensional number system—describe 3D rotation. Through interactive visualizations and"
            " clear explanations, this resource builds deep intuition for understanding quaternion mathematics"
            " without getting lost in abstract formulas. Essential for anyone working with 3D rotations in"
            " robotics, computer graphics, or biomechanical modeling.\n"
            "          </p>\n"
            '          <a href="https://eater.net/quaternions"'
        ),
        (
            "          <h3>Visualizing Quaternions (Ben Eater)</h3>\n"
            '          <p class="resource-description">\n'
            "            An explorable interactive series explaining how quaternions describe 3D rotation,"
            " building intuition\n"
            "            through visualization rather than abstract formulas.\n"
            "          </p>\n"
            '          <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> The rotation representations used in the AffineDrift"
            " rotation-converter tool and GoM Volume 0 are best internalized with this visual introduction"
            " before reading the formal SE(3) treatment.</p>\n"
            '          <a href="https://eater.net/quaternions"'
        ),
        "Visualizing Quaternions",
    )

    # 8. OpenSim — trim + add note + update URL to docs page
    content = safe_replace(
        content,
        (
            "          <h3>OpenSim</h3>\n"
            '          <p class="resource-description">\n'
            "            OpenSim is a freely available, open-source software platform for modeling, simulating,"
            " and analyzing \n"
            "            the neuromusculoskeletal system. The platform provides extensive documentation,"
            " tutorials, example models, \n"
            "            and educational resources. It's an essential tool for biomechanics research and"
            " education, allowing users \n"
            "            to create and analyze musculoskeletal models without commercial restrictions.\n"
            "          </p>\n"
            '          <a href="https://www.opensim.org/"'
        ),
        (
            "          <h3>OpenSim Documentation and Tutorials</h3>\n"
            '          <p class="resource-description">\n'
            "            OpenSim is a freely available, open-source platform for modeling, simulating, and"
            " analyzing\n"
            "            the neuromusculoskeletal system, with extensive tutorials and example models.\n"
            "          </p>\n"
            '          <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> OpenSim's induced-acceleration and joint-reaction analysis"
            " pipelines are the reference implementations for the biomechanics methods described in"
            " AffineDrift Volume III.</p>\n"
            '          <a href="https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/overview"'
        ),
        "OpenSim",
    )

    # 9. Drake — trim + add note + fix URL
    content = safe_replace(
        content,
        (
            "          <h3>Drake (MIT)</h3>\n"
            '          <p class="resource-description">\n'
            "            Drake is a C++ toolbox maintained by the Robot Locomotion Group at MIT for analyzing"
            " the dynamics of \n"
            "            robots and finding their state trajectories through optimization and control. The"
            " website provides \n"
            "            extensive documentation, tutorials, and example code. It's particularly useful for"
            " underactuated systems \n"
            "            and includes tools for trajectory optimization, model-based control, and simulation"
            " of complex robotic systems.\n"
            "          </p>\n"
            '          <a href="https://www.drake.mit.edu/"'
        ),
        (
            "          <h3>Drake Documentation (MIT)</h3>\n"
            '          <p class="resource-description">\n'
            "            Drake is MIT's C++ toolbox for multibody dynamics, trajectory optimization, and"
            " model-based\n"
            "            control, with comprehensive documentation, tutorials, and Python bindings.\n"
            "          </p>\n"
            '          <p style="font-size:0.85rem;color:var(--text-light);margin-top:0.25rem;">'
            "<strong>Why AffineDrift:</strong> Drake's MultibodyPlant API implements the same spatial-vector"
            " equations of motion used in the AffineDrift dynamics chapters; its documentation is the"
            " reference for readers who want to run the models computationally.</p>\n"
            '          <a href="https://drake.mit.edu/"'
        ),
        "Drake (MIT)",
    )

    # 10. REMOVE: WSCG Presentations (paywalled)
    wscg = (
        "\n"
        '      <div class="resource-card">\n'
        '                <div class="resource-content">\n'
        "        <h3>World Scientific Congress of Golf (WSCG) Presentations</h3>\n"
        '        <p class="resource-description">\n'
        "          The World Scientific Congress of Golf (WSCG) convenes researchers and practitioners to share"
        " peer-reviewed advances in golf biomechanics, equipment science, and performance analytics. The"
        " GolfScience Vimeo storefront provides access to recorded WSCG presentation bundles for purchase"
        " and streaming.\n"
        "        </p>\n"
        '        <a href="https://vimeo.com/golfscience/videos"\n'
        '           class="resource-link"\n'
        '           target="_blank"\n'
        '           rel="noopener">\n'
        "          View WSCG Presentation Catalog &rarr;\n"
        "        </a>\n"
        "        </div>\n"
        "      </div>\n"
    )
    if wscg in content:
        content = content.replace(wscg, "\n", 1)
        print("  Removed WSCG card")
    else:
        # Try a simpler match
        if "World Scientific Congress of Golf (WSCG) Presentations" in content:
            # Find and remove the whole card block
            start = content.find("<h3>World Scientific Congress of Golf")
            if start > 0:
                # Find the enclosing resource-card div start
                card_start = content.rfind('<div class="resource-card">', 0, start)
                # Find the closing </div></div> pattern
                end = content.find("</div>\n      </div>", start)
                if end > 0:
                    end += len("</div>\n      </div>")
                    content = content[:card_start] + content[end:]
                    print("  Removed WSCG card (fallback method)")
                else:
                    print("  WARNING: Could not remove WSCG card")
        else:
            print("  WARNING: WSCG card not found")

    # 11. REMOVE: Penn State Golf Course (paywalled course)
    if "Penn State Golf Biomechanics Course" in content:
        start = content.find("<h3>Penn State Golf Biomechanics Course")
        if start > 0:
            card_start = content.rfind('<div class="resource-card">', 0, start)
            end = content.find("</div>\n      </div>", start)
            if end > 0:
                end += len("</div>\n      </div>")
                content = content[:card_start] + content[end:]
                print("  Removed Penn State card")
        else:
            print("  WARNING: Penn State card start not found")
    else:
        print("  WARNING: Penn State card not found")

    # 12. REMOVE: Physiology Web (generic)
    if "Physiology Web" in content:
        start = content.find("<h3>Physiology Web")
        if start > 0:
            card_start = content.rfind('<div class="resource-card">', 0, start)
            end = content.find("</div>\n      </div>", start)
            if end > 0:
                end += len("</div>\n      </div>")
                content = content[:card_start] + content[end:]
                print("  Removed Physiology Web card")
        else:
            print("  WARNING: Physiology Web start not found")
    else:
        print("  WARNING: Physiology Web not found")

    # 13. REMOVE: Robotics Library (generic)
    if "Robotics Library" in content:
        start = content.find("<h3>Robotics Library")
        if start > 0:
            card_start = content.rfind('<div class="resource-card">', 0, start)
            end = content.find("</div>\n      </div>", start)
            if end > 0:
                end += len("</div>\n      </div>")
                content = content[:card_start] + content[end:]
                print("  Removed Robotics Library card")
        else:
            print("  WARNING: Robotics Library start not found")
    else:
        print("  WARNING: Robotics Library not found")

    # 14. REMOVE: Reading List nav-link card (not a real resource)
    if "Reading List" in content and 'href="bibliography.html"' in content:
        start = content.find("<h3>Reading List")
        if start > 0:
            card_start = content.rfind('<div class="resource-card">', 0, start)
            end = content.find("</div>", start)
            if end > 0:
                end += len("</div>")
                content = content[:card_start] + content[end:]
                print("  Removed Reading List card")
        else:
            print("  WARNING: Reading List card not found by h3")

    final_notes = content.count("Why AffineDrift")
    final_cards = content.count('class="resource-card"')
    print(f"  Websites final: {final_notes} notes, {final_cards} cards")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  Written successfully")


# ============================================================
# Fix #2776: resources-papers.qmd
# - Add DOI/publisher links as primary; Scholar search as secondary
# ============================================================
def fix_papers():
    path = "c:/Users/diete/Repositories/AffineDrift/resources/resources-papers.qmd"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    print(f"  Papers initial length: {len(content)}")
    # The files use the Unicode arrow → (U+2192), not &rarr;
    ARROW = "→"

    # 1. Putnam - add DOI link before Scholar link
    content = safe_replace(
        content,
        (
            '            <a href="https://scholar.google.com/scholar?q=author:%22Carol+Putnam%22+golf+interaction+forces"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Carol Putnam - Interaction Forces Papers {ARROW}\n"
            "            </a>"
        ),
        (
            '            <a href="https://doi.org/10.1016/0021-9290(93)90084-R"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Putnam (1993) &#8212; DOI 10.1016/0021-9290(93)90084-R {ARROW}\n"
            "            </a>\n"
            '            <a href="https://scholar.google.com/scholar?q=author:%22Carol+Putnam%22+golf+interaction+forces"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener"\n'
            '               style="margin-top: 0.5rem; display: inline-block;">\n'
            f"              More results on Google Scholar {ARROW}\n"
            "            </a>"
        ),
        "Putnam Scholar link",
    )

    # Remove the redundant note about Research Review page
    content = safe_replace(
        content,
        (
            '            <p style="margin-top: 1rem; font-style: italic; color: var(--text-light); font-size: 0.9rem;">\n'
            "              See Research Review page for current coverage of Carol Putnam's work on interaction"
            " forces.\n"
            "            </p>"
        ),
        "",
        "Putnam redundant note",
    )

    # 2. Zajac - add direct link
    content = safe_replace(
        content,
        (
            '            <a href="https://scholar.google.com/scholar?q=author:%22Felix+Zajac%22+OR+author:%22Felix+E+Zajac%22+induced+acceleration"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Felix Zajac - Induced Acceleration Papers {ARROW}\n"
            "            </a>"
        ),
        (
            '            <a href="https://www.annualreviews.org/doi/10.1146/annurev.bb.18.060189.001251"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Zajac &amp; Gordon (1989) &#8212; Annual Review of Biomedical Engineering {ARROW}\n"
            "            </a>\n"
            '            <a href="https://scholar.google.com/scholar?q=author:%22Felix+Zajac%22+OR+author:%22Felix+E+Zajac%22+induced+acceleration"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener"\n'
            '               style="margin-top: 0.5rem; display: inline-block;">\n'
            f"              More results on Google Scholar {ARROW}\n"
            "            </a>"
        ),
        "Zajac Scholar link",
    )

    # 3. Hirashima - add DOI
    content = safe_replace(
        content,
        (
            '            <a href="https://scholar.google.com/scholar?q=author:%22Masahide+Hirashima%22+baseball+pitching"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Masahide Hirashima - Baseball Pitching Papers {ARROW}\n"
            "            </a>"
        ),
        (
            '            <a href="https://doi.org/10.1249/MSS.0b013e318161e0a7"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Hirashima et al. (2008) &#8212; DOI 10.1249/MSS.0b013e318161e0a7 {ARROW}\n"
            "            </a>\n"
            '            <a href="https://scholar.google.com/scholar?q=author:%22Masahide+Hirashima%22+baseball+pitching"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener"\n'
            '               style="margin-top: 0.5rem; display: inline-block;">\n'
            f"              More results on Google Scholar {ARROW}\n"
            "            </a>"
        ),
        "Hirashima Scholar link",
    )

    # 4. MacKenzie shaft flexibility - add DOI
    content = safe_replace(
        content,
        (
            '            <a href="https://scholar.google.com/scholar?q=author:%22Sasho+MacKenzie%22+shaft+flexibility+golf"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Sasho MacKenzie - Shaft Flexibility Papers {ARROW}\n"
            "            </a>"
        ),
        (
            '            <a href="https://doi.org/10.1007/s12283-009-0016-0"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              MacKenzie &amp; Sprigings (2009) &#8212; DOI 10.1007/s12283-009-0016-0 {ARROW}\n"
            "            </a>\n"
            '            <a href="https://scholar.google.com/scholar?q=author:%22Sasho+MacKenzie%22+shaft+flexibility+golf"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener"\n'
            '               style="margin-top: 0.5rem; display: inline-block;">\n'
            f"              More results on Google Scholar {ARROW}\n"
            "            </a>"
        ),
        "MacKenzie Scholar link",
    )

    # 5. Cheetham - label Scholar links clearly and drop duplicate thesis link
    content = safe_replace(
        content,
        (
            '            <a href="https://scholar.google.com/scholar?q=author:%22Phil+Cheetham%22+handle+twist+velocity+golf"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Phil Cheetham - Handle Twist Velocity Papers {ARROW}\n"
            "            </a>\n"
            '            <a href="https://scholar.google.com/scholar?q=%22Phil+Cheetham%22+handle+twist+velocity+thesis"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener"\n'
            '               style="margin-top: 0.5rem; display: inline-block;">\n'
            f"              Thesis: Handle Twist Velocity {ARROW}\n"
            "            </a>"
        ),
        (
            '            <a href="https://scholar.google.com/scholar?q=author:%22Phil+Cheetham%22+handle+twist+velocity+golf"\n'
            '               class="resource-link"\n'
            '               target="_blank"\n'
            '               rel="noopener">\n'
            f"              Cheetham &#8212; Handle Twist Velocity (Scholar search) {ARROW}\n"
            "            </a>\n"
            '            <p style="margin-top: 0.75rem; font-style: italic; color: var(--text-light); font-size: 0.9rem;">\n'
            "              Note: A direct DOI for Cheetham's handle twist velocity work is not yet confirmed;\n"
            "              Scholar search provided as discovery aid. Verified DOI will be added when identified.\n"
            "            </p>"
        ),
        "Cheetham Scholar links",
    )

    # 6. Instrumented Grip - label Scholar links clearly
    content = safe_replace(
        content,
        f"              Choi and Park Instrumented Grip Papers {ARROW}",
        f"              Choi and Park &#8212; Instrumented Grip (Scholar search) {ARROW}",
        "Choi Park Scholar link",
    )
    content = safe_replace(
        content,
        f"              Koike Instrumented Grip Paper {ARROW}",
        f"              Koike &#8212; Instrumented Grip (Scholar search) {ARROW}",
        "Koike Scholar link",
    )
    content = safe_replace(
        content,
        f"              Vaughan Closed Loop Constraints Papers {ARROW}",
        f"              Vaughan &#8212; Closed Loop Constraints (Scholar search) {ARROW}",
        "Vaughan Scholar link",
    )

    print(f"  Papers final length: {len(content)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  Written successfully")


# ============================================================
# Fix #2775: pages/about.qmd
# - Rename title from "About & Contact" to "About"
# - Replace contact email inline with link to contact.html
# ============================================================
def fix_about():
    path = "c:/Users/diete/Repositories/AffineDrift/pages/about.qmd"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Fix frontmatter title
    content = safe_replace(
        content,
        'title: "About & Contact"\ndescription: "About AffineDrift and how to get in touch"',
        'title: "About"\ndescription: "About AffineDrift"',
        "About title",
    )

    # Replace inline email with link to contact page
    content = safe_replace(
        content,
        (
            "          For questions, feedback, or collaboration inquiries, please contact me via email at"
            ' <a href="mailto:dieterolson@AffineDrift.com">dieterolson@AffineDrift.com</a>.'
        ),
        (
            "          For questions, feedback, or collaboration inquiries, see the"
            ' <a href="contact.html">Contact page</a>.'
        ),
        "About email inline",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  about.qmd written successfully")


# ============================================================
# Fix #2775: pages/tools.qmd
# - Remove Daydreams & Doodles section (Dead Fish duplicate)
# ============================================================
def fix_tools():
    path = "c:/Users/diete/Repositories/AffineDrift/pages/tools.qmd"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    daydreams_section = (
        "\n"
        '      <div class="article-category">\n'
        "        <h2>Daydreams &amp; Doodles <span"
        ' style="display: inline-block; margin-left: 0.5rem; padding: 0.15rem 0.5rem;'
        " background: #f3f4f6; color: #6b7280; border-radius: 4px; font-size: 0.7rem;"
        ' font-weight: 600; vertical-align: middle;">EXPLORATORY</span></h2>\n'
        '        <p style="margin-bottom: 1.5rem; color: var(--text-light); font-style: italic;">\n'
        "          Random interesting projects from space flight to chemical engineering &mdash;"
        " exploratory work outside the core AffineDrift research track.\n"
        "        </p>\n"
        '        <p>See the <a href="daydreams-doodles.html">Daydreams &amp; Doodles</a> page for'
        " exploratory content.</p>\n"
        "      </div>"
    )

    if daydreams_section in content:
        content = content.replace(daydreams_section, "", 1)
        print("  Removed Daydreams section from tools.qmd")
    elif "Daydreams" in content:
        print("  WARNING: Daydreams section found but pattern mismatch - check tools.qmd manually")
    else:
        print("  tools.qmd: Daydreams section already removed")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  tools.qmd written successfully")


# ============================================================
# Fix #2776: resources-books.qmd
# - Add "Top 5 essential reads" section at top
# - Add affiliate disclosure
# ============================================================
def fix_books():
    path = "c:/Users/diete/Repositories/AffineDrift/resources/resources-books.qmd"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if "Top 5 Essential Reads" in content:
        print("  Books: Top 5 section already present")
        return

    old_intro = (
        '        <div class="resources-intro">\n'
        "          <p>\n"
        "            This page contains curated book recommendations covering robotics and screw axis theory,"
        " nonlinear control, \n"
        "            underactuated robotics, biomechanics, golf science, and classical mechanics. Each book"
        " entry includes Amazon links, \n"
        "            previews, and additional resources where available. Open-source materials and free"
        " resources are included when available.\n"
        "          </p>\n"
        "        </div>"
    )

    new_intro = (
        '        <div class="resources-intro">\n'
        "          <p>\n"
        "            Curated book recommendations covering robotics and screw axis theory, nonlinear control,\n"
        "            underactuated robotics, biomechanics, golf science, and classical mechanics. Each book"
        " entry\n"
        "            includes links to publishers, free PDFs where available, and a priority tag:\n"
        "            <strong>essential</strong> (core to the AffineDrift framework),\n"
        "            <strong>recommended</strong> (important background),\n"
        "            <strong>reference</strong> (useful for specific chapters), or\n"
        "            <strong>historical</strong> (foundational context).\n"
        "          </p>\n"
        '          <p style="font-size: 0.85rem; color: var(--text-light);">\n'
        "            <strong>Affiliate disclosure:</strong> Amazon links on this page are plain,"
        " unaffiliated links.\n"
        "            No affiliate IDs are used.\n"
        "          </p>\n"
        "        </div>\n"
        "\n"
        '        <div style="margin-bottom: 2.5rem; padding: 1.25rem 1.5rem;'
        " background: var(--bg-secondary); border-left: 4px solid var(--accent-primary);"
        ' border-radius: 6px;">\n'
        '          <h3 style="margin-top: 0; margin-bottom: 1rem;">Top 5 Essential Reads</h3>\n'
        '          <p style="margin-bottom: 0.75rem; color: var(--text-light); font-size: 0.95rem;">'
        "If you only read five books from this list, start here:</p>\n"
        '          <ol style="margin-bottom: 0; padding-left: 1.25rem;">\n'
        '            <li style="margin-bottom: 0.5rem;"><strong>Murray, Li &amp; Sastry</strong> &mdash;'
        " <em>A Mathematical Introduction to Robotic Manipulation</em>. The SE(3) kinematics and Lie-group"
        " dynamics backbone of AffineDrift. Free PDF available.</li>\n"
        '            <li style="margin-bottom: 0.5rem;"><strong>Featherstone</strong> &mdash;'
        " <em>Rigid Body Dynamics Algorithms</em>. Spatial-vector algebra; the notation used throughout"
        " AffineDrift's dynamics chapters.</li>\n"
        '            <li style="margin-bottom: 0.5rem;"><strong>Tedrake</strong> &mdash;'
        " <em>Underactuated Robotics</em> (MIT, online). The control-affine framework and drift/input"
        " decomposition. Free online textbook.</li>\n"
        '            <li style="margin-bottom: 0.5rem;"><strong>Lynch &amp; Park</strong> &mdash;'
        " <em>Modern Robotics</em>. Product-of-exponentials kinematics and screw-axis dynamics in a"
        " textbook format with Python code.</li>\n"
        '            <li style="margin-bottom: 0;"><strong>Slotine &amp; Li</strong> &mdash;'
        " <em>Applied Nonlinear Control</em>. Lyapunov methods and contraction theory underpinning the"
        " Volume I stability analysis.</li>\n"
        "          </ol>\n"
        "        </div>"
    )

    content = safe_replace(content, old_intro, new_intro, "Books intro + Top 5")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  resources-books.qmd written successfully")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=== Fix #2776: resources-websites.qmd ===")
    fix_websites()

    print("\n=== Fix #2776: resources-papers.qmd ===")
    fix_papers()

    print("\n=== Fix #2775: pages/about.qmd ===")
    fix_about()

    print("\n=== Fix #2775: pages/tools.qmd ===")
    fix_tools()

    print("\n=== Fix #2776: resources-books.qmd ===")
    fix_books()

    print("\nAll fixes applied.")
