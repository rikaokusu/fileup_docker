// [定数] webpack の出力オプションを指定します

// output.pathに絶対パスを指定する必要があるため、pathモジュールを読み込んでおく
const path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');


// モード値を production に設定すると最適化された状態で、
// development に設定するとソースマップ有効でJSファイルが出力される
const MODE = "development";

// ソースマップの利用有無(productionのときはソースマップを利用しない)
const enabledSourceMap = MODE === "development";


module.exports = {

  // モード値を production に設定すると最適化された状態で、
  // development に設定するとソースマップ有効でJSファイルが出力される
  mode: MODE,

  // メインのJS
  entry: "./static/main.js",
  // 出力ファイル
  output: { // コンパイルされたファイルの設定
      path: path.resolve('./static/'),
      // filename: "bundle-[hash].js",
      filename: "bundle.js",
      assetModuleFilename: 'webfont/[hash][ext][query]'
  },
  module: {
    rules: [
      {
        // 対象となるファイルの拡張子(cssのみ)
        test: /\.css$/,
        // Sassファイルの読み込みとコンパイル
        use: [
          // スタイルシートをJSからlinkタグに展開する機能
          "style-loader",
          // CSSをバンドルするための機能
          {
            loader: "css-loader",
            options: {
              // オプションでCSS内のurl()メソッドの取り込みを禁止する
              url: true,
              // ソースマップを有効にする
              sourceMap: enabledSourceMap
            }
          },
          //PostCSSのための設定
          {
            loader: "postcss-loader",
            options: {
              // PostCSS側でもソースマップを有効にする
              sourceMap: true,
              postcssOptions: {
                plugins: [
                  // Autoprefixerを有効化
                  // ベンダープレフィックスを自動付与する
                  require("autoprefixer")({
                    grid: true
                  })
                ]
              }
            }
          }
        ]
      },
      {
        test: /\.scss$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          },
          'resolve-url-loader',
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true
            }
          }
        ]
      },
      // {
      //   // Fontを扱う処理
      //   test: /\.(woff(2)?|ttf|woff|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
      //   use: [{
      //     loader: 'file-loader',
      //     options: {
      //       name: '[name].[ext]',
      //       outputPath: './webfonts',
      //       // ここをDjangoのStatic配下のディレクトリに合わせる必要がある
      //       publicPath: '/static/webfonts',
      //     }
      //   }]
      // },
      {
        test: /\.(png|jpe?g|gif|svg|eot|ttf|woff|woff2)(\?.*$|$)/i,
         // More information here https://webpack.js.org/guides/asset-modules/
        type: "asset",
      },      // {
      //   // imageをバンドルする
      //   test: /\.(jpg|png|gif|woff|ttf)$/,
      //   loaders: 'url-loader'
      // },

      // {
      //   // imageをバンドルする
      //   test: /\.(jpg|png|gif)$/,
      //   use: [{
      //       loader: 'url-loader',
      //   }]
      // },

      // {
      //   // jqueryを$またはjQueryで利用するため
      //   test: require.resolve('jquery'),
      //   use: [{
      //       loader: 'expose-loader',
      //       options: 'jQuery'
      //   }, {
      //       loader: 'expose-loader',
      //       options: '$'
      //   }]
      // },
      // {
      //   // momentをmoment()で利用するため
      //   test: require.resolve('moment'),
      //   use: [{
      //       loader: 'expose-loader',
      //       options: 'moment'
      //   }]
      // },
      {
      // jqueryを$またはjQueryで利用するため
      test: require.resolve("jquery"),
        loader: "expose-loader",
        options: {
          exposes: ["$", "jQuery"],
        },
      },
      {
      // momentをmoment()で利用するため
      test: require.resolve("moment"),
        loader: "expose-loader",
        options: {
          exposes: ["moment"],
        },
      },
      {
      // DropzoneをDropzone()で利用するため
      test: require.resolve('Dropzone'),
          loader: 'expose-loader',
          options: {
            exposes: ["Dropzone", "dropzone"],
        },
      },
      // {
      //   // DropzoneをDropzone()で利用するため
      //   test: require.resolve('Dropzone'),
      //   use: [{
      //       loader: 'expose-loader',
      //       options: 'Dropzone'
      //     }, {
      //         loader: 'expose-loader',
      //         options: 'dropzone'
      //     }]
      // }
    ]
  },
  plugins: [
    // new BundleTracker({filename: './webpack-stats.json'}),
    // jqueryを$またはjQueryで利用するため
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        'window.jQuery': 'jquery',
        moment: 'moment',
        Popper: ['popper.js', 'default'],
        process: 'process/browser',
      }),
  ]
}
