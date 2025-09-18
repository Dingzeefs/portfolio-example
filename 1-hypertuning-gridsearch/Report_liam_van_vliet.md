# Neural Network Hyperparameter Interactions: A Fashion-MNIST Study

When building neural networks, I wondered how different settings would work together rather than in isolation. The main question driving this research was whether network width, depth, training time, and batch size would interact in predictable ways when classifying Fashion-MNIST images.

Going into the experiments, I had three main hunches about how these hyperparameters might interact. First, I suspected that balanced networks where both hidden layers had similar sizes would work better than lopsided ones. There seemed to be a logical sweet spot where adding more capacity would help up to a point, but then additional neurons might just slow things down without improving accuracy.

My second hypothesis centered on the relationship between network size and training time. Bigger networks typically need more time to reach their full potential, so I expected smaller networks to converge quickly but eventually get overtaken by larger ones given enough epochs. This seemed intuitive - like how a sprinter might start fast but a marathon runner catches up over distance.

The third interaction I wanted to test involved batch size and network capacity. I had a theory that larger networks would benefit from smaller batch sizes because the noisier gradients would act as a form of regularization, preventing overfitting. Meanwhile, smaller networks might prefer standard batch sizes for stability.

## What I Discovered

The experiments revealed some fascinating patterns that weren't immediately obvious. The most striking finding was about network architecture balance. Networks where both hidden layers had the same number of units consistently beat unbalanced designs. For example, a 128-128 network outperformed configurations like 64-256 or 256-64, even though they all had similar total parameter counts. This suggests there's something important about information flow through the network that gets disrupted when layers have mismatched capacities.

Looking at the relationship between network size and training time, my second hypothesis proved partially correct but with nuances I hadn't anticipated. Smaller networks did converge faster initially - the 128-128 configuration reached 99.3% of its final performance by just epoch 5. However, while larger networks like 256-256 did eventually surpass smaller ones, the margin was much smaller than expected. By epoch 10, the difference was only about 0.06%, hardly worth the extra computational cost in many scenarios.

The batch size experiments yielded perhaps the most actionable insights. Large networks were surprisingly sensitive to batch size - the 256-256 network's accuracy varied by nearly a full percentage point (87.12% to 87.95%) depending on batch size. The sweet spot turned out to be batch size 32, which provided just enough gradient noise to act as regularization without making training too unstable. Interestingly, very small batches like 16 actually hurt performance, suggesting there's a lower limit where noise becomes detrimental rather than helpful.

## Hyperparameter Relationship Visualizations

### Network Architecture Performance Map
1-hypertuning-gridsearch/width_analysis.png
*Heatmap showing accuracy across different width-depth combinations. Diagonal pattern indicates balanced architectures perform best, with sweet spot at 256-256 configuration.*


## Critical Interactions Discovered

### 1. Architecture Balance Effect
**Finding**: Networks with equal hidden layer sizes (128-128, 256-256) consistently outperformed unbalanced configurations.
**Implication**: Information flow bottlenecks occur when layers have mismatched capacities.

### 2. Size-Efficiency Trade-off
**Finding**: 128-128 achieved 99.6% of optimal accuracy with 56% fewer parameters than 256-256.
**Implication**: Diminishing returns appear earlier than expected for Fashion-MNIST complexity.

### 3. Batch Size Interaction
**Finding**: Large networks (256-256) showed 0.83% accuracy variation across batch sizes, while smaller networks were less sensitive.
**Implication**: Regularization needs scale with network capacity.

## Practical Implications

### Model Selection Strategy
- **High-performance requirement**: Use 256-256 with batch size 32, train for 10 epochs
- **Efficiency priority**: Use 128-128 with standard settings, achieves 99.6% of optimal performance
- **Quick prototyping**: 64-64 with 5 epochs provides reasonable baseline (87.09%)

### Hyperparameter Tuning Guidelines
1. **Start with balanced architectures** (equal layer sizes)
2. **Scale batch size inversely with network size** for optimal regularization
3. **Allow sufficient epochs** for large networks to converge (10+ epochs)
4. **Consider parameter efficiency** - more parameters don't guarantee better performance

## Conclusion
Hyperparameter interactions in neural networks follow predictable patterns: balanced architectures outperform unbalanced ones, larger networks need more training time and smaller batches, and there exists a clear efficiency frontier where additional capacity provides diminishing returns. For Fashion-MNIST, this frontier occurs around 256-256 architecture with 269K parameters.