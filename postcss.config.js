module.exports = {
  plugins: [
    require('postcss-merge-rules')(),  // Merges duplicate rules
    require('css-declaration-sorter')({ order: 'smacss' }),  // Sorts properties
  ],
};