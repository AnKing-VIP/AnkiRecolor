/* global Recolor */

window.Recolor = {}
Recolor.withConfig = function (confstr) {
  Recolor.conf = JSON.parse(confstr)
  const conf = JSON.parse(confstr)
  const colors = conf.colors.sass.day
  for (const colorName in colors) {
    const colorEntry = colors[colorName]
    document.documentElement.style.setProperty(colorName, colorEntry[1])
  }
}
