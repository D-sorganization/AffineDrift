# Markerless Motion Capture — Research Dossier

Compiled 2026-08-02 for `articles/technology-motion-capture.qmd`. Claims not verifiable
from a primary source are flagged `[unverified]`.

---

## 1. Systems

### Theia3D (Theia Markerless Inc.) — the research reference standard

**Pipeline** ([docs](https://docs.theiamarkerless.com/theia3d-documentation/getting-started/theia3d-basics)):

1. Deep networks predict **2D positions of 124 keypoints** per body, every frame, every camera.
2. Calibration → multi-view triangulation into 3D landmarks.
3. A **scaled subject-specific inverse-kinematics skeletal model** (17 rigid segments) is fit to the landmark cloud. **Critical architectural point:** Theia3D does _not_ output raw triangulated keypoints — it outputs the pose of a constrained articulated model, which is what makes segment _orientations_ available at all.

**Camera requirements:** minimum 6 cameras, **8+ recommended**; each joint visible in **≥3 cameras**; subject ≥500 px tall; resolution under 4 MP; **hardware frame synchronization mandatory**; loose clothing degrades tracking; CUDA GPU required.

**Frame rate guidance from Theia:** **60–120 Hz walking, 80–180 Hz running, 180–360 Hz pitching.** The single most important number for a golf article — Theia themselves put a rotational high-velocity throwing motion at 180–360 Hz.

### OpenCap (Stanford)

[Uhlrich et al., _PLoS Comput Biol_ 19(10):e1011462, 2023](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1011462)

Four stages: (1) 2D keypoints via OpenPose or HRNet, **20 keypoints at 60 Hz**; (2) **LSTM marker augmenter** mapping 20 sparse keypoints → 43 anatomical markers, trained on **108 hours of mocap**, held-out error **8.0 mm** — worth ~**3.4°** of accuracy (4.5° with, 7.9° without); (3) OpenSim scaling + IK, 33 DOF; (4) muscle-driven dynamic simulation.

Cameras 2–10 m from subject (**<2 m causes pose-detector failures**). Adding cameras beyond two gave **<0.3° improvement**.

### Others

| System                      | Notes                                                                                                                                              |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **KinaTrax**                | Now redirects to [Hawk-Eye Innovations Biomechanics](https://www.hawkeyeinnovations.com/biomechanics). **No public quantitative accuracy claims.** |
| **Vicon Shōgun Markerless** | Explicitly an **entertainment/VFX product**, not a clinical pipeline. **Vicon makes no quantitative accuracy claim for markerless.**               |
| **Qualisys Miqus Video**    | 1080p@120 fps, 720p@**480 fps**; commonly the camera front end for Theia3D                                                                         |
| **DARI Motion**             | Built on **Captury**; claims "world's only **FDA-cleared** markerless solution." **No camera count, frame rate, or error figures published.**      |
| **Simi Shape**              | Silhouette/shape fitting; vendor site TLS failure `[unverified]`                                                                                   |

---

## 2. Pose estimation backbones

**Bottom-up** (OpenPose): detect all keypoints then group; runtime independent of person count. **Top-down** (HRNet, ViTPose, RTMPose): person detector then per-crop pose; higher accuracy. Essentially all modern high-accuracy work is top-down.

| Network                    | Key idea                                                 | Benchmark                                            |
| -------------------------- | -------------------------------------------------------- | ---------------------------------------------------- |
| **OpenPose** (2019)        | Bottom-up, **Part Affinity Fields**                      | [arXiv:1812.08008](https://arxiv.org/abs/1812.08008) |
| **HRNet** (CVPR 2019)      | **Maintains high-resolution representations throughout** | [arXiv:1902.09212](https://arxiv.org/abs/1902.09212) |
| **ViTPose** (NeurIPS 2022) | Plain ViT backbone, 100M→1B params                       | **81.1 mAP COCO test-dev**                           |
| **RTMPose** (2023)         | Deployment-oriented                                      | RTMPose-m **75.8 AP**, 90+ FPS CPU                   |
| **BlazePose/MediaPipe**    | Mobile, **33 keypoints**, world landmarks via **GHUM**   | >30 FPS on Pixel 2                                   |
| **DeepLabCut** (2018)      | Transfer learning, ~200 labeled frames                   | [arXiv:1804.03142](https://arxiv.org/abs/1804.03142) |

### What COCO accuracy actually means — the crucial caveat

COCO AP is computed against **OKS**, whose per-keypoint tolerances were set by _human annotator disagreement_, not anatomy. **A network at 81 mAP is 81 mAP at reproducing what crowdworkers clicked.**

Wade et al.: labels come from "labelers from the general population who likely do not possess anatomical knowledge," "two people may have very different interpretations of a joint center," occluded joints get "labelled onto points that are biomechanically incorrect" — therefore "it is unwise to expect pose estimation algorithms to match marker-based methods when the labelled data they are trained on is fundamentally flawed" ([_PeerJ_ 10:e12995](https://pmc.ncbi.nlm.nih.gov/articles/PMC8884063/)).

---

## 3. Monocular vs multi-camera

**Triangulation floor:** with **eight virtual cameras, perfect calibration, no motion blur, no distortion**, Pose2Sim still gave mean joint-angle error **3.0° walking, 4.1° running, 4.0° cycling**, with a **15° systematic hip-flexion offset** and OpenPose "systematic joint center offsets up to 50 mm" ([_Sensors_ 22(7):2712](https://pmc.ncbi.nlm.nih.gov/articles/PMC9002957/)). That is the floor imposed by keypoint definition alone.

**Why monocular is structurally weaker:** depth ambiguity (a keypoint constrains a ray, resolved by a _learned pose prior_ — a liability for unusual postures like golf address); scale ambiguity (reconstruction is up to global scale); and long-axis rotation nearly unobservable.

Wade et al.: multi-camera OpenPose joint centres **10–50 mm** from marker-based; **monocular 3D generally 40–60 mm**, best 30–40 mm.

### The head-to-head benchmark

[Li Z, Shin S, Phan V, Meinders E, Halilaj E, _IEEE TBME_ 2026](https://doi.org/10.1109/TBME.2025.3622032) — **13 single-view and 2 multi-view** systems vs marker-based, 23 adults:

- **OpenCap (2 cameras) beat WHAM (monocular) by 1.7°** (p < 0.0001)
- **Theia3D (10 cameras) beat OpenCap by 1.3°** (p < 0.0001)

> **Monocular → 2-camera buys ~1.7°; 2-camera → 10-camera buys another ~1.3°.** Both small relative to the ~4–6° baseline, which says the bottleneck is keypoint/joint definition, **not camera count**.

---

## 4. Body models — SMPL joints are NOT anatomical joint centres

[Keller M, Werling S, Shin S, Delp S, Pujades S, Liu CK, Black MJ. **"From Skin to Skeleton: Towards Biomechanically Accurate 3D Digital Humans."** _ACM TOG_ 42(6), SIGGRAPH Asia 2023](https://skel.is.tue.mpg.de/)

SKEL's premise is that SMPL and descendants "employ **simplified kinematic structures that do not correspond to the true joint locations**." SMPL joints are _regressed from mesh vertices_ to make the surface deform plausibly — optimized for skinning quality, not anatomical fidelity. SMPL cannot properly represent knee flexion or **forearm supination**, because its DOF structure does not match the actual articulations.

> Any pipeline reporting "hip rotation" or "forearm rotation" from an SMPL-family fit is reporting a quantity its own body model is architecturally incapable of representing correctly. **Separate from and additional to the label problem.**

Related: SMPL-X (+hands/face), STAR (sparse pose correctives, 20% of SMPL parameters), VIBE (adversarial motion prior on AMASS), HMR 2.0 / 4D-Humans (transformerized, strong on unusual poses).

---

## 5. Validation numbers

### Kanko et al. — the Theia3D series (Queen's University)

**(a) Concurrent validity** ([_J Biomech_ 127:110665, 2021](https://pubmed.ncbi.nlm.nih.gov/34380101/)): 30 adults, treadmill, **8 video + 7 infrared cameras simultaneously**. **Joint centre RMSD < 2.5 cm for all joints except hip at 3.6 cm.** **Global segment pose RMSD < 5.5° for all segment angles _except those representing rotations about the long axis_.**

**(b) Inter-session repeatability** ([_J Biomech_ 121:110422](https://www.sciencedirect.com/science/article/abs/pii/S0021929021002025)): 8 adults, **3 sessions ~8.5 days apart**, own clothing. Inter-trial variability **2.5°**; **inter-session 2.8° — smaller than all previously reported marker-based values**; variability ratio 1.1.

> Markerless _repeatability_ beats marker-based because there is no marker re-placement step. **A precision win, not an accuracy win.**

**(c) Spatiotemporal** ([PMID 33915475](https://pubmed.ncbi.nlm.nih.gov/33915475/)): "good to excellent agreement" except **poor for stance time, double limb support time, and stride width**.

**(d) Clothing** ([PMID 35749889](https://pubmed.ncbi.nlm.nih.gov/35749889/)): athletic vs street clothing — segment-length differences **0.2–0.9 cm**; mean joint-angle deviation **2.6°**. Caveat: this was _walking_, not a golfer in loose kit at swing speeds.

### OpenCap validation

| Metric                               | Value                             |
| ------------------------------------ | --------------------------------- |
| Mean kinematic error, 2-camera HRNet | **4.5° MAE** (range 1.7–10.3°)    |
| Without LSTM augmentation            | 7.9°                              |
| Mean per-marker error                | **32 mm** (upper extremity 39 mm) |
| Peak GRF error                       | 6.2 %BW (vertical 11.4 %BW)       |

**Authors' own limitations:** validated only on healthy young adults _simulating_ pathology; augmenter "may not generalize beyond its training distribution"; **test–retest reliability was not measured**; kinematic errors **approach the magnitude of skin-marker artefact itself**, making further improvement hard to even demonstrate.

**Since 2023:** meta-analysis pooled **RMSE 5.877°** ([_Biology of Sport_ 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC12954493/)); scoping review median RMSE hip sagittal 5.99°, knee sagittal 6.07°, **upper limb 13.81–52.17°**, **RMSE >100% under severe occlusion**, **30% trial exclusion rates**, max 240 Hz "insufficient for high-speed transient movements". ACL drop-jump: frontal knee RMSE >6°, "**OpenCap currently cannot be recommended for ACL re-injury risk assessment**".

### Needham et al. 2021 — the mm-level backbone comparison

[_Sci Rep_ 11:20673](https://pmc.ncbi.nlm.nih.gov/articles/PMC8526586) — 9× JAI SP5000c at 200 Hz + 15-camera Qualisys, controlled lighting.

3D joint centre error (mm), OpenPose / AlphaPose / DeepLabCut:

| Joint    | Walking      | Running      | Jumping      |
| -------- | ------------ | ------------ | ------------ |
| Shoulder | 29/30/24     | 27/31/29     | 32/34/33     |
| **Hip**  | **34/31/43** | **29/32/45** | **36/36/53** |
| Knee     | 30/31/42     | **41/48/58** | 29/27/35     |
| Ankle    | 16/19/30     | 23/36/52     | 14/14/15     |

- **Hip and knee showed the largest systematic differences for all methods.** Root cause stated explicitly: "**large-scale mislabeling of hip joint centre locations in the datasets used to train each deep learning model**."
- **Ankle was best** — a joint centre "easier to identify and label." Performance tracks _label quality_, not joint difficulty.
- **Running worst, jumping best** — and this held even at 200 Hz with controlled lighting.

### Wade et al. 2022 — mechanisms named

[_PeerJ_ 10:e12995](https://pmc.ncbi.nlm.nih.gov/articles/PMC8884063/): temporospatial comparable to marker-based, but "**joint center locations and joint angles are not yet sufficiently accurate for clinical applications.**"

- **Theia3D: 2.6–11° flexion/extension and ab/adduction; 6.9–13.2° for rotation.**
- Marker-based reference itself: joint centre errors up to **30 mm**, averaging 9–19 mm — **the "gold standard" is not gold.**
- Hip internal/external rotation errors "possibly as high as **21.8°**."

**The geometric proof:** algorithms "only extract **two points on each segment** (proximal and distal joint center locations), **whilst three keypoints are required to calculate 6DoF**." A segment defined by two endpoints has an undetermined roll. Proposed fix: "manually relabeling training data with an additional third keypoint location on each segment."

**On soft tissue artefact:** markerless "**may reduce**" STA "**although this is yet to be examined experimentally.**" Markerless does not remove inferring bone pose from a moving skin surface — it replaces a discrete-landmark STA model with a **learned, whole-surface inference whose error structure is unmapped**. Different error, not less error.

### Error pattern across all studies

1. **Spatiotemporal: excellent** (ICC 0.92–0.99)
2. **Sagittal flexion/extension: good, ~2–6°**
3. **Frontal: worse, ~3–9°**
4. **Transverse/long-axis: bad to catastrophic**, 5–15°+ typical, up to 21.8° (hip IE), ±15.75° LoA (cutting), 23° (elbow IE, boxing), Theia transverse RMSE range **3.16°–56.61°**
5. **Ankle and hip systematically worst**

**Two further distinctions:**

- **Offset vs shape.** Wren et al. found **all RMSD < 8° after offset correction**. Much of markerless error is constant bias, not waveform distortion → far better at _within-subject change detection_ than _absolute value_ reporting.
- **Precision > accuracy.** Kanko (2.8° inter-session) and Outerleys (1.45°) show markerless repeatability beats marker-based. Markerless trades a **random** error source for a **systematic** one.

---

## 6. Golf and high-speed sport

### The golf evidence base is thin

**Sportsbox AI 3DGolf:** claims 3D from a **single phone video**, ">30 key points on body, club and ball." Phone requirements, frame rate, and any quantitative error figure **not disclosed**.

> **A Europe PMC full-text search for "Sportsbox" returns zero results.** There is **no peer-reviewed validation of Sportsbox AI 3DGolf in the indexed biomedical literature.**

That absence matters because it is _the worst-case configuration for the measurand golfers care about_: a **monocular** system estimating **long-axis rotations** (X-factor) of a **high-velocity** motion. Every one of those three is independently documented as a primary error source, and they compound.

**Published golf markerless work:** [Yamamoto K et al., _Front Sports Act Living_ 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10684732/) — 27 golfers, HRNet-w48 + DeepLabCut for club, **single camera at 240 Hz**, measuring **forward tilt angle** and club trajectory, i.e. deliberately **sagittal-plane 2D quantities only**. Authors' caveats: club-head detection **degrades near impact**; 2D sagittal analysis is "inferior with respect to accuracy compared with 3D." **Note they chose 240 Hz for a single-camera 2D study.**

**No peer-reviewed Theia3D golf-swing validation was located.** `[unverified]` — a real gap.

### Baseball as the best proxy

[Aguinaldo AL et al., _J Sports Sci_ 44(10):1374–1388, 2026](https://doi.org/10.1080/02640414.2025.2595411) — 18 collegiate pitchers, Hawk-Eye and Theia3D vs marker-based. **MPJPE 56.6 ± 9.4 mm (Hawk-Eye), 52.0 ± 12.3 mm (Theia3D).** Stride length agreed best; **shoulder rotational measures most variable.**

> These are **~2× the Kanko walking joint-centre errors** (25–36 mm). **Speed costs roughly a factor of two in joint-centre error.**

### Motion blur and temporal resolution

- **Theia's own guidance: 180–360 Hz for pitching.** OpenCap runs at **60 Hz** — a phone app at 60 Hz through a ~0.25 s downswing captures roughly **15 frames of the entire motion**.
- **Blur is set by exposure time, not frame interval.** Needham used controlled lighting specifically to minimize blur at 200 Hz and _still_ found running produced the largest errors.
- **Domain shift in temporal content:** COCO/MPII are _still images_ of everyday activity. No motion-blur augmentation matched to 100 mph segment velocities, no golf-posture coverage.
- Unanimous across the literature: **error scales with segment velocity and with direction-change sharpness.** A golf downswing is the extreme of both.

### Sport-review aggregate

[Adlou B, Wilburn C, Weimar W, _Sensors_ 25(14):4384, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12299843/): markerless **sagittal 3–15°, frontal 2.12–9.14°, transverse 3.16°–56.61°**; single-camera "often exceeding 20° error for complex movements"; markerless **cannot track sports implements** alongside the body; OpenCap ~**215× cheaper** than a traditional lab.

---

## 7. Fundamental limitations

**7.1 Bone long-axis rotation is not observable from the surface** — three stacking causes: _geometric_ (two points per segment, three required for 6DoF); _physical_ (skin near the rotation axis barely moves — a femur can internally rotate 20° with almost no silhouette change); _model-structural_ (SMPL-family models lack the DOF).

**7.2 Training-label error is the dominant systematic bias.** Because the bias is _in the labels_, more data, bigger models and higher COCO AP **do not fix it** — they converge more confidently onto the wrong point. This is why only ~3° separates a monocular network from a 10-camera rig.

**7.3 No physical calibration of joint centres.** Marker-based has functional joint-centre calibration and palpation; markerless has none — the joint centre is wherever the network says.

**7.4 Domain shift** — golf attire, postures, and environments are underrepresented or absent in training corpora.

**7.5 Keypoint definition inconsistency** — OpenPose (25), COCO-17, BlazePose (33), Theia3D (124) do not agree on what "hip" means. Results from two markerless systems are **not interchangeable**.

**7.6 Consumer hardware limits** — 60 Hz, auto-exposure, rolling shutter, no hardware sync. Theia requires hardware frame sync; phones do not have it.

**7.7 Occlusion** — 30% trial exclusion rates and RMSE >100° under severe occlusion. In golf the trail arm and pelvis are occluded through much of the swing.

**7.8 STA is replaced, not eliminated** (see §5).

**7.9 The reference standard is itself imperfect** — marker-based joint centres carry up to 30 mm error. Markerless error has approached this level, so **further improvement can no longer be cleanly demonstrated** against a marker-based criterion.

---

## Suggested framing

> Multi-camera markerless (Theia3D-class, 8+ synchronized cameras at 180–360 Hz) is a legitimate research instrument whose _repeatability exceeds_ marker-based (2.8° inter-session) while its _accuracy_ is 2–6° sagittal, 3–9° frontal, and unreliable in the transverse plane. Joint-centre error roughly doubles (25–36 mm → 52–57 mm) from walking to pitching speeds.
>
> Two-phone systems (OpenCap) are ~4.5° MAE on slow tasks at 60 Hz and explicitly not recommended for tasks as fast as a drop jump.
>
> Single-phone consumer golf apps have **no published validation**, use the configuration most vulnerable to every documented failure mode, and target the exact rotational measurands the technology handles worst.
>
> The right use is **longitudinal within-golfer change detection**, where systematic offsets cancel. The wrong use is absolute measurement of X-factor, hip rotation, or any long-axis quantity.

## Gaps flagged

- `[unverified]` No peer-reviewed validation of **Sportsbox AI 3DGolf** (Europe PMC: zero hits).
- `[unverified]` No **Theia3D golf-swing** validation study located.
- `[unverified]` **Simi Shape**, **Contemplas**, **Uplift Labs** — sites unreachable, no validation located.
- `[unverified]` Absolute Human3.6M MPJPE figures for VideoPose3D / MotionBERT.
