# -*- coding: UTF-8 -*-

import constants as ct
from tests import test_env


def main():
    test_env.check(ct.SAMPLE_GEOJSON_PATH)


if __name__ == "__main__":
    main()
