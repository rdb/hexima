#version 150

/**
 * Contains code from https://github.com/Jam3/glsl-fast-gaussian-blur
 * This code is under the MIT license.
 */

uniform sampler2D image;
uniform vec2 direction;
uniform float scale;
uniform vec4 p3d_ColorScale;

out vec4 p3d_FragData[1];

void main() {
  vec2 resolution = textureSize(image, 0) - vec2(1, 1);
  vec2 uv = gl_FragCoord.xy / resolution;
  vec4 color = vec4(0.0);
  vec2 off1 = vec2(1.411764705882353) * direction * scale;
  vec2 off2 = vec2(3.2941176470588234) * direction * scale;
  vec2 off3 = vec2(5.176470588235294) * direction * scale;
  color += texture(image, uv) * 0.1964825501511404;
  color += texture(image, uv + (off1 / resolution)) * 0.2969069646728344;
  color += texture(image, uv - (off1 / resolution)) * 0.2969069646728344;
  color += texture(image, uv + (off2 / resolution)) * 0.09447039785044732;
  color += texture(image, uv - (off2 / resolution)) * 0.09447039785044732;
  color += texture(image, uv + (off3 / resolution)) * 0.010381362401148057;
  color += texture(image, uv - (off3 / resolution)) * 0.010381362401148057;
  color.a = 1.0;
  p3d_FragData[0] = color * p3d_ColorScale;
}
