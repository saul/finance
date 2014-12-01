/*!
 * Bootstrap's Gruntfile
 * http://getbootstrap.com
 * Copyright 2013-2014 Twitter, Inc.
 * Licensed under MIT (https://github.com/twbs/bootstrap/blob/master/LICENSE)
 */

module.exports = function (grunt) {
  'use strict';

  var os = require('os');

  // Force use of Unix newlines
  grunt.util.linefeed = '\n';

  // Project configuration.
  grunt.initConfig({

    // Metadata.
    bsPkg: grunt.file.readJSON('bootstrap_package.json'),
    pkg: grunt.file.readJSON('package.json'),
    banner: '/*!\n' +
    ' * <%= pkg.name %> v<%= pkg.version %>\n' +
    ' *\n' +
    ' * This application also incorporates code from:\n' +
    ' * Bootstrap v<%= bsPkg.version %> (<%= bsPkg.homepage %>)\n' +
    ' * Copyright 2011-<%= grunt.template.today("yyyy") %> <%= bsPkg.author %>\n' +
    ' * Licensed under <%= bsPkg.license.type %> (<%= bsPkg.license.url %>)\n' +
    ' */\n',
    distDir: 'static_dist',

    // Task configuration.
    clean: {
      dist: '<%= distDir %>'
    },

    jshint: {
      options: {
        jshintrc: 'static_src/js/.jshintrc'
      },
      bs: {
        src: 'static_src/js/bs/*.js'
      },
      core: {
        src: 'static_src/js/*.js'
      }
    },

    jscs: {
      options: {
        config: 'static_src/js/.jscsrc'
      },
      bs: {
        src: '<%= jshint.bs.src %>'
      },
      core: {
        src: '<%= jshint.core.src %>'
      }
    },

    concat_sourcemap: {
      options: {
        separator: ';'
      },
      dist: {
        src: [
          'static_src/js/bs/transition.js',
          'static_src/js/bs/alert.js',
          'static_src/js/bs/button.js',
          'static_src/js/bs/carousel.js',
          'static_src/js/bs/collapse.js',
          'static_src/js/bs/dropdown.js',
          'static_src/js/bs/modal.js',
          'static_src/js/bs/tooltip.js',
          'static_src/js/bs/popover.js',
          'static_src/js/bs/scrollspy.js',
          'static_src/js/bs/tab.js',
          'static_src/js/bs/affix.js',
          'static_src/js/datavis.js',
          'static_src/js/navbar.js',
          'static_src/js/transaction-table.js',
        ],
        dest: '<%= distDir %>/js/finance.js'
      }
    },

    uglify: {
      options: {
        banner: '<%= banner %>',
        sourceMap: true,
        sourceMapIncludeSources: true,
        preserveComments: 'some'
      },
      dist: {
        files: {
          '<%= distDir %>/js/finance.min.js': '<%= concat_sourcemap.dist.src %>'
        }
      }
    },

    less: {
      options: {
        strictMath: true,
        sourceMap: true,
        sourceMapURL: 'finance.css.map',
        sourceMapFilename: '<%= distDir %>/css/<%= less.options.sourceMapURL %>',
        sourceMapRootpath: '/',
        outputSourceFiles: true
      },
      dist: {
        src: 'static_src/less/finance.less',
        dest: '<%= distDir %>/css/finance.css'
      }
    },

    autoprefixer: {
      options: {
        browsers: [
          'Android 2.3',
          'Android >= 4',
          'Chrome >= 20',
          'Firefox >= 24', // Firefox 24 is the latest ESR
          'Explorer >= 8',
          'iOS >= 6',
          'Opera >= 12',
          'Safari >= 6'
        ],
        map: true
      },
      dist: {
        src: '<%= distDir %>/css/finance.css'
      }
    },

    csslint: {
      options: {
        csslintrc: 'static_src/less/.csslintrc'
      },
      dist: [
        '<%= distDir %>/css/finance.css'
      ]
    },

    cssmin: {
      options: {
        compatibility: 'ie8',
        keepSpecialComments: '*',
        noAdvanced: true
      },
      dist: {
        src: '<%= distDir %>/css/finance.css',
        dest: '<%= distDir %>/css/finance.min.css'
      }
    },

    usebanner: {
      options: {
        position: 'top',
        banner: '<%= banner %>'
      },
      files: {
        src: '<%= distDir %>/css/*.css'
      }
    },

    csscomb: {
      options: {
        config: 'static_src/less/.csscomb.json'
      },
      dist: {
        expand: true,
        cwd: '<%= distDir %>/css/',
        src: ['*.css', '!*.min.css'],
        dest: '<%= distDir %>/css/'
      }
    },

    copy: {
      fonts: {
        cwd: 'static_src/',
        src: 'fonts/*',
        dest: '<%= distDir %>/',
        expand: true
      }
    },

    exec: {
      collectstatic: {
        command: function () {
          if (os.platform() == 'win32') {
            return 'call env/Scripts/activate.bat && python manage.py collectstatic --noinput';
          } else {
            return '. macenv/bin/activate && python manage.py collectstatic --noinput';
          }
        },
        stdout: true
      }
    },

    watch: {
      js: {
        files: 'static_src/js/*.js',
        tasks: ['dist-js', 'exec:collectstatic']
      },
      less: {
        files: 'static_src/less/**/*.less',
        tasks: ['dist-css', 'exec:collectstatic']
      }
    }
  });


  require('load-grunt-tasks')(grunt, {scope: 'devDependencies'});

  // JS distribution task.
  grunt.registerTask('dist-js', ['jshint', 'jscs', 'concat_sourcemap', 'uglify']);

  // CSS distribution task.
  grunt.registerTask('dist-css', ['less', 'autoprefixer', 'usebanner', 'csscomb', 'cssmin']);

  // Full distribution task.
  grunt.registerTask('dist', ['clean', 'dist-css', 'copy', 'dist-js', 'exec:collectstatic']);

  // Default task.
  grunt.registerTask('default', ['dist']);
};
