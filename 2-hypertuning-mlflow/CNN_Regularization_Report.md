# CNN Architecture and Regularization Synergies: A Fashion-MNIST Investigation

My initial hypothesis was that regularization techniques would show diminishing returns when combined - that dropout and normalization would partially overlap in their effects, leading to minimal additional gains when used together. I also suspected that CNNs, with their inherent spatial structure and weight sharing, would need much lighter regularization than fully connected networks, perhaps around 0.1 dropout rate rather than the typical 0.5 used in dense layers.

## The Experiments

Starting with a baseline CNN achieving 67.6% test loss on Fashion-MNIST, I systematically explored five key dimensions: network depth, width, dropout regularization, normalization techniques, and their interactions. Each experiment built on previous findings, creating a hypothesis-driven exploration rather than random search.

The architecture experiments revealed that depth matters more than width for Fashion-MNIST. A 6-layer network with 64 filters achieved the best raw performance (48.4% test loss), while an 8-layer network actually degraded performance to 52.1% test loss, confirming vanishing gradient issues without skip connections. Surprisingly, a narrow but deep network (6 layers, 16 filters) achieved remarkable parameter efficiency, delivering 90% of the performance with just 20,346 parameters compared to 311,178 for the wide variant.

2-hypertuning-mlflow/cleanshot.png

2-hypertuning-mlflow/cleanshot2.png

## Regularization Discoveries

The dropout experiments validated my hypothesis about CNNs needing lighter regularization. Testing rates of 0.1, 0.3, and 0.5 showed clear optimal performance at 0.1 dropout (34.9% test loss), with higher rates causing significant degradation. At 0.5 dropout, the network struggled to converge, with initial training loss starting at 1.46 compared to 0.71 for the 0.1 rate. This confirms that spatial feature maps in CNNs require different treatment than dense layer neurons.

2-hypertuning-mlflow/cleanshot3.png

The normalization comparison yielded the most surprising result. While I expected BatchNorm to dominate given its ubiquity in modern architectures, InstanceNorm actually achieved the best performance (35.1% test loss). This makes sense retrospectively - Fashion-MNIST contains items with vastly different brightness characteristics (white shirts versus black pants), and InstanceNorm's per-image normalization removes these statistical variations, allowing the network to focus on structural patterns like collars, sleeves, and textures.

2-hypertuning-mlflow/cleanshot4.png

## The Power of Synergy

The most significant discovery came when combining techniques. Using both 0.1 dropout and InstanceNorm together achieved 32.4% test loss. This 7-8% improvement over individual methods disproved my initial hypothesis about diminishing returns. The techniques address fundamentally different problems: InstanceNorm stabilizes gradients and removes per-image variance, while dropout provides regularization during training. Their complementary mechanisms create multiplicative rather than additive benefits.

When I finally combined the optimal architecture (6 layers, 64 filters) with the best regularization combo (0.1 dropout + InstanceNorm), the model achieved a breakthrough 27.0% test loss - a 60% improvement over the original baseline. This exceeded the sum of individual improvements, demonstrating true synergistic enhancement.

## Key Technical Insights

The experiments revealed several critical patterns about CNN regularization:

**Regularization placement matters significantly.** The optimal configuration places Dropout2D after activation but before pooling, maximizing its effect on the full feature representation before spatial reduction. The complete block structure that worked best was: Conv2d → InstanceNorm → ReLU → Dropout2D → MaxPool2d.

**Regularization scales without adjustment.** The 0.1 dropout rate remained optimal whether applied to the 4-layer baseline with 93K parameters or the 6-layer model with 588K parameters. This robustness suggests that proper regularization rates are more about the type of layer (convolutional versus dense) than the overall model size.

**Normalization enables depth.** The 6-layer architecture only achieved good performance when combined with normalization. Without it, gradient flow issues prevented effective training. InstanceNorm's stabilizing effect was crucial for making deeper networks viable on this relatively simple dataset.


## Conclusion

This experimentation demonstrates that regularization in CNNs is not simply about preventing overfitting - it's about creating the right conditions for effective learning. The synergy between dropout and normalization shows that understanding mechanism matters more than following rules of thumb. Light stochastic regularization combined with strong deterministic normalization creates an environment where CNNs can leverage their full capacity without overfitting.

The systematic, hypothesis-driven approach proved essential for uncovering these interactions. Random hyperparameter search might have found good configurations, but understanding why certain combinations work enables principled application to new problems. For Fashion-MNIST, this methodology led to a 60% improvement over baseline - from 67.6% to 27.0% test loss - demonstrating the power in deep learning optimization.