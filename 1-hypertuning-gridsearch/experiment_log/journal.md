# Hyperparameter Tuning Experiment Log

## Date: 2025-09-18

### Initial Understanding
- **Experiment Goal**: Tune a neural network for Fashion-MNIST classification
- **Dataset**: 60,000 clothing images, 28x28 pixels, 10 classes
- **Base Model**: 3-layer feedforward neural network

---

## Hypotheses

### Hypothesis 1: Network Size vs Performance
**Statement:** "Increasing network size (both width via more units and depth via more layers) will improve accuracy but at the cost of training speed. There may be a point of diminishing returns where additional capacity doesn't help or even hurts performance due to overfitting."

**Reasoning:**
- Bigger networks = more parameters = more capacity to learn complex patterns
- Trade-offs: slower training, more memory usage
- Risk: Overfitting (memorizing training data rather than learning generalizable patterns)

**Planned Test:**
- Compare networks with different widths (units per layer)
- Test adding additional layers (depth)
- Monitor training vs validation accuracy gap to detect overfitting

---

## Key Concepts Learned

### Network Capacity
- **Width**: Number of units (neurons) in each layer
- **Depth**: Number of layers in the network
- Both affect the model's ability to learn complex patterns differently

### Overfitting
- When a model performs well on training data but poorly on new data
- Like a student memorizing answers instead of understanding concepts
- Can be detected by growing gap between training and validation performance

---

## Experimental Modifications

### Modification 1: Added Third Hidden Layer
- Added `units3` parameter to create deeper network
- Purpose: Test if depth improves performance
- Expected outcome: Better feature extraction but potentially slower training

---

## Key Insights

### Width vs Depth Effects
**Width (more units per layer):**
- Like having more "detectors" at each abstraction level
- Captures more variety in patterns in parallel
- Example: 256 units = 256 different feature detectors

**Depth (more layers):**
- Creates hierarchy of understanding
- Each layer builds on previous layer's features
- Layer 1: edges → Layer 2: shapes → Layer 3: objects
- Risk: Vanishing gradient problem (like "telephone game" - signal degradation)

### Student Discovery: Vanishing Gradient Problem
"As you add many layers it actually becomes harder to recognize patterns as it passes through so many layers"
- Correct insight! Gradients can vanish or explode in deep networks
- Information degrades as it backpropagates through many layers
- This is why very deep networks need special techniques (ResNet, batch norm)

---

## Questions to Investigate

1. **Batch Size Trade-offs**: Why use batches of 64 instead of 1 or 60,000?
   - Answer: Balance between gradient stability (not too noisy) and computational efficiency
   - Batch=1: Very noisy updates
   - Batch=60k: Too slow, only one update per epoch
   - Batch=64: Good balance, efficient GPU utilization

2. **Optimal Network Architecture**: What combination of width and depth works best?
   - Need to test: various unit combinations (64, 128, 256, 512)
   - Need to test: 2 vs 3 vs 4 layer networks
   - Hypothesis: 3 layers might perform worse than 2 due to vanishing gradients

3. **Learning Rate Sensitivity**: How does network size affect optimal learning rate?
   - Larger networks might need different learning rates

---

## Experiments

### Experiment 1: Width Grid Search
**Date**: 2025-09-18
**Hypothesis**: "The best performance will be achieved with balanced layer sizes (along the diagonal where units1 ≈ units2). Very large layers might overfit, while very small layers might underfit."

**Setup**:
- Units to test: [32, 64, 128, 256]
- Fixed: 5 epochs, batch_size=64, Adam optimizer, lr=0.001
- Measuring: Validation accuracy

**Expected outcome**: Heatmap will show higher accuracy in the middle-to-upper range, with diminishing returns beyond 256 units.

**Baseline Results** (from initial grid search):
- Best accuracy: 87.17% (256 units config)
- Average accuracy: ~85-86%
- Settings: 3 epochs, full dataset (937 batches), batch_size=64, Adam optimizer

**Student Analysis**:
"It's better for depth and width to be equal in power. With 3 epochs, the smaller 128-128 network had time to tune its weights efficiently. The 256-256 network likely needs more epochs to converge."

**Key Insights from Results**:
1. **Sweet spot found**: 128-128 outperformed 256-256 (87.17% vs 84.68%)
2. **Balance matters**: Networks with equal layer sizes performed better on average
3. **Efficiency wins**: Smaller networks trained faster and generalized better with limited epochs
4. **Parameter count isn't everything**: More parameters ≠ better accuracy

**Follow-up Hypotheses**:
- H2: "256-256 will outperform 128-128 given 10 epochs instead of 3"
- H3: "Smaller batch sizes will improve generalization for larger networks"
- H4: "Optimal learning rate decreases as network size increases"

---

### Experiment 2: Epochs vs Network Size
**Date**: 2025-09-18
**Hypothesis**: "256-256 will outperform 128-128 given 10 epochs instead of 3"

**Results**:
| Epochs | 64-64 | 128-128 | 256-256 |
|--------|-------|---------|---------|
| 3      | 84.88% (7.3s) | 86.90% (9.2s) | **86.97%** (13.0s) |
| 5      | 87.09% (12.4s) | 87.02% (16.2s) | **87.69%** (26.1s) |
| 10     | 87.77% (30.7s) | 88.52% (35.1s) | **88.58%** (40.4s) |

**Key Insights**:
1. **Hypothesis confirmed but nuanced**: 256-256 does win, but the margin shrinks from 0.67% at 5 epochs to only 0.06% at 10 epochs
2. **128-128 catches up fast**: Shows better convergence rate than 256-256
3. **Efficiency matters**: 128-128 achieves 99.93% of 256-256's performance in 87% of the time
4. **Diminishing returns**: All networks plateau around 87-88% accuracy
5. **Training time scales linearly** with network size and epochs

**New Hypothesis**: H5: "128-128 might overtake 256-256 at 15+ epochs due to faster convergence"

**Practical Takeaway**: For this dataset, 128-128 offers the best accuracy/time trade-off

**TensorBoard Analysis**:
Looking at the loss curves in TensorBoard reveals:
1. **Loss stabilization at 7-10 epochs** - curves flatten, indicating convergence
2. **Training vs validation gap** - train loss continues dropping while validation plateaus (early overfitting signs)
3. **128-128 (purple) shows best stability** - lowest validation loss (~0.33) with least volatility
4. **256-256 (orange) similar performance** but more unstable during training
5. **64-64 (green) clearly underfitting** - highest validation loss

**Conclusion**: Models have reached capacity limits at 10 epochs. Additional epochs would likely cause overfitting rather than improvement.

---

### Experiment 3: Depth Variations (2-layer vs 3-layer)
**Date**: 2025-09-18
**Hypothesis H7**: "3-layer networks will underperform 2-layer networks due to vanishing gradients"

**Results**:
| Architecture | Accuracy | Time | Parameters |
|--------------|----------|------|------------|
| 128-128 (2-layer) | **87.67%** | 13.4s | 118,282 |
| 128-128-128 (3-layer) | **87.79%** | 15.6s | 134,794 |
| 256-256 (2-layer) | **87.81%** | 19.8s | 269,322 |
| 256-256-256 (3-layer) | **87.90%** | 21.3s | 335,114 |

**Key Findings**:
1. **Hypothesis DISPROVEN**: 3-layer networks outperformed 2-layer networks in both configurations
2. **Improvement is marginal**: Only 0.09-0.12% accuracy gain
3. **Cost is real**: 14-25% more parameters, 15-16% longer training time
4. **No severe vanishing gradients**: For 3-layer networks on Fashion-MNIST

**Student Insight Revision**:
Original: "As you add many layers it actually becomes harder to recognize patterns"
Corrected: "While vanishing gradients can be a problem, 3 layers don't suffer severely on Fashion-MNIST. The improvements are tiny because the dataset is relatively simple."

**Accuracy vs Efficiency Trade-off**:
- **Pure accuracy winner**: 256-256-256 (87.90%)
- **Efficiency winner**: 128-128 (87.67% with best parameter efficiency)
- **Question**: Is 0.12% accuracy gain worth 14% more parameters?

**Conclusion**: Fashion-MNIST is simple enough that 2-3 layers perform similarly. The dataset doesn't have sufficient complexity to strongly benefit from hierarchical feature learning.

---

### Experiment 4: Extended Width Variations
**Date**: 2025-09-18
**Hypothesis H6**: "Extending the grid to 512-512 and 1024-1024 units will show diminishing returns or overfitting"

**Student Predictions**:
1. "512-512 > 256-256"
2. "1024-1024 = too much (overfitting)"

**Results**:
| Configuration | Accuracy | Time | Parameters | Efficiency (Params/Acc) |
|---------------|----------|------|------------|-------------------------|
| 256-256 | **88.03%** | 22.1s | 269,322 | 3,058 |
| 512-512 | **87.94%** | 28.9s | 669,706 | 7,639 |
| 1024-1024 | **88.35%** | 63.2s | 1,863,690 | 21,059 |

**Key Findings**:
1. **Prediction 1 WRONG**: 512-512 (87.94%) < 256-256 (88.03%) - diminishing returns appeared earlier than expected
2. **Prediction 2 WRONG**: 1024-1024 achieved highest accuracy (88.35%) without severe overfitting
3. **Cost is brutal**: 1024-1024 takes 3x longer and 7x parameters for only +0.32% gain
4. **Sweet spot confirmed**: 256-256 offers best balance of accuracy and efficiency

**Surprise insight**: Fashion-MNIST has enough complexity that very large networks don't overfit as quickly as expected

---

### Experiment 5: Batch Size Effects
**Date**: 2025-09-18
**Hypothesis H8**: "Smaller batch sizes (16, 32) will help larger networks (256-256) generalize better"

**Student Prediction**: "Smaller batches will help 256-256 through implicit regularization"

**Results** (256-256 network):
| Batch Size | Accuracy | Time | Batches/Epoch |
|------------|----------|------|---------------|
| 16 | **87.12%** | 53.4s | 3,750 |
| 32 | **87.95%** | 27.6s | 1,875 |
| 64 | **87.75%** | 19.0s | 937 |
| 128 | **87.60%** | 14.8s | 468 |

**Key Findings**:
1. **Prediction partially correct**: Batch=32 was optimal, confirming smaller can be better
2. **Batch=16 too noisy**: Hurt performance despite more regularization effect
3. **Batch=128 too smooth**: Slightly worse than standard batch=64
4. **Sweet spot**: Batch=32 provides good balance of regularization and stability

**Learning**: Smaller batches help, but there's a lower limit where noise hurts more than regularization helps

---

## Final Summary of All Experiments

### **Accuracy Rankings** (Best to Worst):
1. **1024-1024**: 88.35% (but 63.2s, 1.86M params)
2. **256-256**: 88.03% (22.1s, 269K params)
3. **256-256 + batch=32**: 87.95% (27.6s, 269K params)
4. **256-256-256 (3-layer)**: 87.90% (21.3s, 335K params)
5. **128-128-128 (3-layer)**: 87.79% (15.6s, 135K params)
6. **128-128**: 87.67% (13.4s, 118K params)

### **Efficiency Winner**: 128-128 (87.67% with best time/parameter ratio)
### **Practical Winner**: 256-256 (88.03% with reasonable computational cost)
### **Pure Performance Winner**: 1024-1024 (88.35% but computationally expensive)

---

## Hypotheses for Future Experiments

### Experiment 3: Extended Width Variations
**Hypothesis H6**: "Extending the grid to 512-512 and 1024-1024 units will show diminishing returns or overfitting"

**Intuition**:
- Based on 128-128 vs 256-256 results, larger networks need more time to converge
- Fashion-MNIST (28x28 grayscale) may not have enough complexity to benefit from 512+ units
- Expect: 512-512 might match 256-256 performance but take much longer
- Risk: 1024-1024 likely to overfit with current dataset size

### Experiment 4: Depth Variations (2-layer vs 3-layer)
**Hypothesis H7**: "3-layer networks will underperform 2-layer networks due to vanishing gradients"

**Intuition from student insight**:
"As you add many layers it actually becomes harder to recognize patterns as it passes through so many layers"
- Vanishing gradient problem will hurt 3-layer performance
- Without batch normalization or residual connections, deeper = worse
- Expect: 128-128-128 < 128-128 in final accuracy
- Fashion-MNIST features (edges, textures) don't need deep hierarchical learning

### Experiment 5: Batch Size Effects
**Hypothesis H8**: "Smaller batch sizes (16, 32) will help larger networks (256-256) generalize better"

**Intuition**:
- Large networks + large batches = overfitting to smooth gradients
- Small batches = noisy gradients = implicit regularization
- Expect: 256-256 with batch_size=16 > 256-256 with batch_size=64
- But: 128-128 already well-tuned, so smaller batches won't help much
- Trade-off: Smaller batches = longer training time

**Questions to investigate**:
1. Does batch_size=32 give 256-256 the regularization it needs?
2. Will very small batches (8, 16) hurt 64-64 network (too noisy)?
3. What's the accuracy vs training time trade-off?

---

## Experimental Priority

Based on insights so far:
1. **Depth experiment** (quick, tests fundamental architecture question)
2. **Batch size for 256-256** (might unlock larger network potential)
3. **Extended width** (likely diminishing returns, but completes the picture)

---

## Next Steps
- [x] Run baseline experiment with original architecture
- [x] Test width variations (grid search) - COMPLETED (64,128,256)
- [ ] Test depth variations (add layers) - HIGH PRIORITY
- [ ] Test batch size effects - MEDIUM PRIORITY
- [ ] Test extended width (512, 1024) - LOW PRIORITY
- [ ] Test learning rate sensitivity
- [ ] Test different optimizers
- [x] Analyze results in TensorBoard
- [ ] Document optimal configuration

---

## Notes
- Using TOML serialization for experiment tracking
- TensorBoard for visualization
- Each experiment saved with timestamp in `modellogs/`


CleanShot 2025-09-18 at 18.17.09@2x.png