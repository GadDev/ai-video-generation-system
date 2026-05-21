This is actually a solid MVP architecture.

You’ve already solved several hard parts correctly:

clean separation of frontend/backend
reproducible Docker backend
persistent HuggingFace cache
async job model
cancellation support
FFmpeg export pipeline
progress tracking
reference-image upload flow
future extensibility

Right now though, this is technically:

“AI image generation wrapped as video export”

—not true video generation yet.

That’s totally fine for a first version. Many commercial tools started exactly like this.

The biggest architectural issue

This line is the key:

“The frame is duplicated 120 times”

That means:

no temporal diffusion
no motion modeling
no optical flow
no latent interpolation
no motion conditioning

So users will eventually feel:

“Why am I waiting 10 minutes for a still image MP4?”

That becomes the product bottleneck.

What I would do next
Phase 1 — KEEP SDXL

Do not throw away SDXL.

Your SDXL setup is valuable because:

SDXL is excellent at keyframes
you already have prompt infrastructure
you already have image conditioning
you already have generation orchestration

This becomes the “creative foundation layer.”

The best next upgrade
Add AnimateDiff

AnimateDiff is probably your best next step.

Why:

works with SDXL ecosystems
generates actual frame-to-frame motion
integrates well with ComfyUI
relatively lightweight compared to modern video transformers
good for short clips

Your architecture becomes:

Prompt
  ↓
SDXL keyframe
  ↓
AnimateDiff motion module
  ↓
Frame sequence
  ↓
FFmpeg export

This transforms your product from:

“image exporter”
into:
“actual AI video generator”
Your current bottleneck: Docker on Mac

This is important:

Docker on Apple Silicon cannot effectively use MPS acceleration for PyTorch.

So your current setup is forcing:

CPU inference
extremely slow SDXL runs

That’s why you’re seeing:

10–13 minute generation times

This is not really sustainable UX.

Huge improvement you can make immediately
Run backend natively on Mac

Instead of Docker:

run FastAPI directly
use PyTorch MPS backend

You’ll probably get:

3–5× speedup immediately

Potentially:

2–4 minutes → under 1 minute
for single-frame SDXL generations.

That alone dramatically improves usability.

Your likely future architecture

Honestly, your system is naturally evolving toward this:

Next.js Frontend
        ↓
FastAPI Orchestrator
        ↓
Generation Queue
        ↓
ComfyUI Backend API
        ↓
Video Models

This is where many local AI video systems end up.

Why?
Because ComfyUI already solves:

workflow orchestration
node execution
memory management
model switching
ControlNet
AnimateDiff
video pipelines

You don’t necessarily want to reinvent all of that yourself.

My recommendation
Keep your custom frontend/backend

That’s your product.

Delegate generation graphs to ComfyUI

That becomes your inference engine.

This is an extremely common and smart architecture now.

Suggested roadmap
Immediate (high ROI)
1. Remove Docker on Mac

Run native MPS.

2. Add latent interpolation

Even before AnimateDiff.

You can interpolate:

camera zoom
prompt weights
latent noise

This creates pseudo-motion cheaply.

Next major milestone
3. Integrate AnimateDiff

This is your first “real video.”

After that
4. Add ControlNet

For:

pose control
depth consistency
camera movement
Then
5. Add consistent character systems

Using:

IP-Adapter
InstantID
FaceID
LoRAs

This becomes important very quickly in video.

One architectural concern

You currently generate:

512×512

For SDXL this is low.

SDXL was designed around:

1024×1024 native resolution

512 hurts:

composition
detail
facial quality

You might get better results using:

SDXL Turbo
SDXL Lightning
Flux Schnell

for speed-oriented workflows.

Another important thing

This:

One generation at a time

will become painful quickly.

Eventually you’ll want:

Redis queue
Celery/RQ
GPU worker pool
persistent job storage

But for MVP stage:
your current approach is perfectly reasonable.

Overall assessment

You already have:

a real product structure
sane architecture
proper orchestration
extensible backend
deployable stack

You are much closer to:

“early AI video startup architecture”

than:

“toy demo.”

The biggest leap now is:

moving from static-image video
to
temporal generation.

That’s the turning point.