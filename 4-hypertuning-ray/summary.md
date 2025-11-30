# Summary: Hyperparameter Tuning Project
# CNN Optimization on CIFAR-10: When Simple Beats Complex

My initial hypothesis was that transfer learning with pretrained ResNet18 would dramatically outperform any custom CNN architecture on CIFAR-10, achieving 92-94% accuracy by leveraging ImageNet's 1.2 million training images. I also expected that deeper networks (5+ layers) would naturally learn better hierarchical features, and that modern activation functions like GELU would universally improve performance.

**I was wrong on almost every count.**

## The Experiments

Starting with a baseline 2-layer CNN achieving ~75% validation accuracy on CIFAR-10, I systematically explored seven dimensions: network depth, regularization, data augmentation, architecture capacity (depth × width), activation functions, learning rate scheduling, and transfer learning. Each experiment built on previous findings, creating a hypothesis-driven exploration across 30+ hours of training.

The journey from 75% to 84.30% accuracy revealed that for small images (32×32), conventional deep learning wisdom often doesn't apply.

## Experiment 1: Depth Optimization

**Hypothesis:** 3-4 convolutional layers would outperform shallower and deeper networks.

**Results:**
| Depth | Val Acc | Overfitting Gap | Parameters |
|-------|---------|-----------------|------------|
| 2 layers | 75.5% | 0.6% | 545k |
| 3 layers | 80.7% | 1.7% | 357k |
| 4 layers | **83.4%** | 10.1% | 522k |
| 5 layers | 82.6% | 15.7% | 1.6M |

**Key Discovery:** The hypothesis was confirmed, but the mechanism surprised me. Five layers didn't suffer from vanishing gradients (BatchNorm + Adam prevented that) - instead, they suffered from *excessive memorization*. The 98.3% training accuracy proved the network was powerful enough; it just couldn't generalize.

**Unexpected Finding:** 3 layers used *fewer* parameters (357k) than 2 layers (545k) yet performed 5% better. Deeper models allocate parameters more efficiently to convolutional layers rather than bloated fully-connected layers.

## Experiment 2: Regularization

**Hypothesis:** Higher dropout (0.4-0.5) combined with BatchNorm would reduce the 10% overfitting gap from Experiment 1.

**Results:**
| Dropout | BatchNorm | Val Acc | Gap |
|---------|-----------|---------|-----|
| 0.0 | True | 81.97% | 17.98% |
| 0.3 | True | **83.03%** | 10.16% |
| 0.5 | True | 81.16% | **5.88%** |
| 0.5 | False | 79.63% | 7.55% |

**Hypothesis Status:** REJECTED

**Key Discovery:** The hypothesis predicted dropout=0.4 would be optimal, but it actually *hurt* performance (-0.46% vs 0.3). The experiment revealed a fundamental accuracy-generalization tradeoff: you cannot achieve both ≥83% accuracy AND <5% gap with the 4-layer architecture. Every 1% gap reduction costs ~0.3-0.5% validation accuracy.

**The Real Issue:** 4 layers with 522k parameters is simply too much capacity for CIFAR-10's 50k training images (10.4 params per training sample). Even aggressive regularization can't fully solve structural over-parameterization.

## Experiment 3: Data Augmentation

**Hypothesis:** Data augmentation (RandomCrop, RandomHorizontalFlip, ColorJitter) would boost accuracy to ~86% and reduce overfitting.

**Results:**
| Strategy | Val Acc | Gap |
|----------|---------|-----|
| None | 82.96% | 10.82% |
| Light | 83.03% | 10.82% |
| Medium | 83.07% | 11.21% |
| Strong | **83.28%** | 10.46% |

**Hypothesis Status:** REJECTED

**Key Discovery:** All augmentation strategies performed nearly identically. The +0.32% accuracy improvement was within noise. This "failed" experiment was actually a success - it proved that **architecture matters more than data augmentation** for this task. The model hit a performance ceiling that data diversity alone cannot overcome.

## Experiment 6: Architecture Capacity (Depth × Width)

**Hypothesis:** Wider shallow networks (3L × 48F) would match deeper narrow networks (5L × 16F) in accuracy but with better generalization.

**Results (12 configurations):**

| Config | Val Acc | Gap | Params |
|--------|---------|-----|--------|
| 3L × 16F | 77.69% | **1.49%** | 156k |
| 3L × 48F | **81.68%** | 6.90% | 604k |
| 4L × 48F | 82.17% | 14.31% | 1,072k |
| 5L × 32F | 79.57% | 15.91% | 928k |

**Hypothesis Status:** PARTIALLY CONFIRMED

**Key Discovery:** The Pareto winner was **3L × 48F** - achieving 81.68% accuracy with only 6.90% gap. Critically, 3L×48F nearly matched 4L×48F (81.68% vs 82.17%) with **half the overfitting** (6.90% vs 14.31%).

**The Universal Approximation Insight:** Width can compensate for depth. For 32×32 images, you only need a 3-level feature hierarchy (edge → texture → object), but you need sufficient representational capacity (48 filters) to capture CIFAR-10's 10 diverse classes.

## Experiment 4: Activation Functions

**Hypothesis:** Modern activation functions (GELU, Leaky ReLU) would outperform standard ReLU.

**Results:**
| Activation | Val Acc | Gap |
|------------|---------|-----|
| ReLU | 82.77% | **6.13%** |
| Leaky ReLU | 83.35% | 8.17% |
| GELU | **84.30%** | 11.32% |

**Hypothesis Status:** PARTIALLY CONFIRMED

**Key Discovery:** GELU achieved the highest accuracy (84.30%) but with nearly 2× the overfitting compared to ReLU. This creates a Pareto front:
- **High accuracy + high overfitting:** GELU
- **Lower accuracy + better generalization:** ReLU
- **Sweet spot:** Leaky ReLU (83.35%, 8.17% gap)

**Why ReLU Generalizes Better:** Dead neurons create sparse representations - a form of implicit regularization that prevents memorization. GELU's smooth gradients enable learning complex decision boundaries that don't generalize as well.

## Experiment 5: Learning Rate Scheduling

**Hypothesis:** Adaptive learning rates would improve both accuracy and generalization.

**Results:**
| Scheduler | Val Acc | Gap |
|-----------|---------|-----|
| Fixed LR | 77.03% | **6.50%** |
| CosineAnnealing | 79.98% | 13.18% |
| StepLR | 80.95% | 16.51% |
| ReduceLROnPlateau | **81.42%** | 17.28% |

**Hypothesis Status:** PARTIALLY CONFIRMED (but counterproductive)

**Key Discovery:** Schedulers improved accuracy by 3-4% but caused **catastrophic overfitting**, tripling the train-val gap (6.5% → 17%). Low learning rates in later epochs enable fine-grained memorization rather than generalization.

**Critical Comparison:** Experiment 4 (activation functions) outperformed Experiment 5 by +1.93% accuracy with *half* the overfitting. **Activation function choice is a stronger lever than LR scheduling for small datasets.**

## Experiment 7: Transfer Learning with ResNet18

**Hypothesis:** Pretrained ResNet18 would achieve 92-94% accuracy, breaking the 84% ceiling.

**Results:**
| Model | Val Acc | Gap | Params |
|-------|---------|-----|--------|
| Custom CNN (GELU) | **84.30%** | 11.32% | 604k |
| ResNet18 (Frozen) | 42.20% | 0.50% | 11.2M |
| ResNet18 (Fine-tuned) | 82.20% | **3.70%** | 11.2M |

**Hypothesis Status:** REJECTED

**Key Discovery:** This was the most surprising result. ResNet18 achieved only 82.20% - **worse than our custom CNN** (84.30%)! The frozen backbone performed terribly (42%) because ImageNet features learned at 224×224 resolution don't transfer well to 32×32 images.

**The Silver Lining:** ResNet18 achieved much better generalization (3.70% gap vs 11.32%). If generalization matters more than peak accuracy, fine-tuned ResNet18 is the better choice.

**Why Transfer Learning Failed:** The 32×32 resolution creates a domain gap that pretrained ImageNet features cannot bridge. ResNet's early convolutional layers with large receptive fields lose too much information on tiny images.

## The Power of Systematic Optimization

The progression across all experiments:

| Experiment | Technique | Best Accuracy | Key Lesson |
|------------|-----------|---------------|------------|
| Baseline | 2-layer CNN | 75.5% | Starting point |
| Exp 1 | Depth optimization | 83.4% | 4 layers optimal for accuracy |
| Exp 2 | Regularization | 83.0% | Can't fix architectural overfitting |
| Exp 3 | Data augmentation | 83.3% | Minimal impact at ceiling |
| Exp 6 | Capacity analysis | 81.7% | Width > depth for small images |
| Exp 4 | Activation functions | **84.30%** | GELU wins but overfits |
| Exp 5 | LR scheduling | 81.4% | Counterproductive without regularization |
| Exp 7 | Transfer learning | 82.2% | Image size compatibility matters |

**Total improvement:** 75.5% → 84.30% = **+8.8% accuracy**

## Key Technical Insights

### 1. For Small Images (32×32), Width > Depth
CIFAR-10 images only need a 3-level feature hierarchy. Adding more layers creates optimization problems without corresponding representational benefits. Compensate with wider layers (48 filters) instead of deeper networks.

### 2. Regularization Cannot Fix Architectural Over-parameterization
Dropout=0.5 reduced overfitting by half (10% → 6% gap) but also dropped accuracy by 2%. The 4-layer architecture has fundamental excess capacity that regularization cannot fully address.

### 3. Activation Functions Are More Powerful Than LR Scheduling
For small datasets like CIFAR-10:
- GELU: +1.53% accuracy over ReLU
- Best LR scheduler: +4% accuracy but +11% more overfitting

Activation function choice gave better results with less overfitting penalty.

### 4. Transfer Learning Requires Image Size Compatibility
ResNet18 pretrained on 224×224 ImageNet images cannot effectively transfer features to 32×32 CIFAR-10. The domain gap is too large. For transfer learning to work, either:
- Use images ≥224×224
- Upscale small images before feeding to pretrained models
- Train a custom architecture from scratch

### 5. The Accuracy-Generalization Tradeoff is Fundamental
Across all experiments, improvements in validation accuracy consistently came with increased overfitting gaps. There is no free lunch - you must choose your priority.

## Conclusion

This experimentation demonstrates that conventional deep learning wisdom doesn't always apply to small images. The hypothesis that ResNet18 would dominate was **completely wrong** - a well-tuned 3-layer CNN with GELU activation achieved the best accuracy (84.30%) with 18× fewer parameters.

The systematic, hypothesis-driven approach proved essential for understanding *why* certain combinations work:
- **Architecture matters most** for breaking performance ceilings
- **Activation functions matter more than training hyperparameters** for small datasets
- **Transfer learning isn't always better** - image size compatibility is critical

For CIFAR-10 production:
- **Best accuracy:** Custom 3L×48F + GELU (84.30%, 604k params)
- **Best generalization:** ResNet18 fine-tuned (82.20%, 3.70% gap)
- **Best efficiency:** Custom CNN - 18× smaller AND 2% more accurate

The key insight: **domain-specific optimization beats generic pretrained models** for small images. Understanding when to apply transfer learning versus building custom architectures is more valuable than blindly following best practices.

---

Find the [notebook](./hypertuning_experiments.ipynb)

[Go back to Homepage](../../README.md)
