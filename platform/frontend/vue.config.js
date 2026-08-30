const { defineConfig } = require('@vue/cli-service'); // Import this helper if using Vue CLI
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const analyzerConfig = require('./src/config/analyzer.config.js');
const path = require('path'); // Need to import the path module

// Decide whether to enable the analyzer based on the environment variable
const plugins = [];
if (process.env.ANALYZE) {
  plugins.push(new BundleAnalyzerPlugin(analyzerConfig));
}

module.exports = {
  publicPath: process.env.VUE_APP_PUBLIC_PATH || "/",
  transpileDependencies: ["vuetify"],
  css: {
    loaderOptions: {
      scss: {
        additionalData: '@import "@/styles/index.scss";'
      }
    }
  },
  configureWebpack: {
    module: {
      rules: [
        // Babel transpilation rule for the marked library
        {
          test: /\.js$/, // Match JavaScript files
          // Explicitly restrict this to files from the marked library under node_modules
          include: path.resolve(__dirname, 'node_modules/marked'),
          use: {
            loader: 'babel-loader',
            options: {
              // Use the config from the project's root babel.config.js, or specify a preset inline here
              // Usually it's fine to just use the project's existing Babel config
            }
          }
        },
        {
          test: /\.worker\.js$/,
          use: {
            loader: 'worker-loader',
            options: { inline: 'no-fallback' }
          }
        }
      ]
    },
    plugins
  },
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: process.env.VUE_APP_SRV || 'http://localhost:3000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    },
    headers: {
      'Access-Control-Allow-Origin': '*'
    }
  }
};